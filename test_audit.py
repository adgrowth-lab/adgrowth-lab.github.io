#!/usr/bin/env python3
"""
Unit tests for audit.py (TikTok Ads Cold-Start & Anti-Leak Audit Suite)
"""

import os
import sys
import tempfile
import unittest
import subprocess
import json

from audit import (
    audit_pangle_leak,
    parse_traffic_csv,
    evaluate_cold_start,
    evaluate_spend_match,
    TIERS
)


class TestAuditPangle(unittest.TestCase):
    def test_pangle_critical_leak(self):
        # 90% pangle traffic
        res = audit_pangle_leak(
            total_spend=500.0,
            tiktok_clicks=2500,
            site_sessions=2000,
            pangle_sessions=1800
        )
        self.assertEqual(res["verdict"], "CRITICAL HIJACK")
        self.assertEqual(res["pangle_ratio_pct"], 90.0)
        self.assertEqual(res["wasted_spend"], 450.0)
        self.assertEqual(res["real_effective_spend"], 50.0)
        self.assertEqual(res["real_sessions"], 200)
        self.assertAlmostEqual(res["reported_cpc"], 0.20, places=2)
        self.assertAlmostEqual(res["effective_cpc"], 2.50, places=2)

    def test_pangle_clean_traffic(self):
        res = audit_pangle_leak(
            total_spend=1000.0,
            tiktok_clicks=2000,
            site_sessions=1900,
            pangle_sessions=0
        )
        self.assertEqual(res["verdict"], "CLEAN TRAFFIC")
        self.assertEqual(res["wasted_spend"], 0.0)
        self.assertEqual(res["pangle_ratio_pct"], 0.0)

    def test_pangle_zero_inputs(self):
        res = audit_pangle_leak(
            total_spend=0.0,
            tiktok_clicks=0,
            site_sessions=0,
            pangle_sessions=0
        )
        self.assertEqual(res["wasted_spend"], 0.0)
        self.assertEqual(res["reported_cpc"], 0.0)

    def test_csv_parser(self):
        with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False) as f:
            f.write("Referrer,Sessions,Bounce_Rate\n")
            f.write("tiktok.com,300,45%\n")
            f.write("pangleglobal,700,98%\n")
            f.write("google,100,50%\n")
            f_path = f.name

        try:
            total, pangle = parse_traffic_csv(f_path)
            self.assertEqual(total, 1100)
            self.assertEqual(pangle, 700)
        finally:
            if os.path.exists(f_path):
                os.remove(f_path)


class TestColdStartEvaluator(unittest.TestCase):
    def test_perfect_campaign_score(self):
        res = evaluate_cold_start(
            daily_budget=300.0,
            target_cpa=25.0,  # 12x ratio
            objective="purchase",
            placement="tiktok_only",
            format_type="spark_ads",
            hook_type="creator_face_direct",
            sound="voiceover_trending"
        )
        self.assertEqual(res["survival_score"], 100)
        self.assertEqual(res["status"], "READY TO SCALE")
        self.assertEqual(len(res["deductions"]), 0)

    def test_flawed_campaign_penalties(self):
        # Budget starvation ($20 budget on $30 CPA), ATC pixel poisoning, Automatic placement (Pangle), static logo hook, muted
        res = evaluate_cold_start(
            daily_budget=20.0,
            target_cpa=30.0,
            objective="atc",
            placement="automatic",
            format_type="dark_post",
            hook_type="logo_intro",
            sound="muted"
        )
        # 100 - 30(budget) - 35(ATC) - 25(auto placement) - 20(logo) - 20(muted) - 10(dark post) = 0
        self.assertEqual(res["survival_score"], 0)
        self.assertEqual(res["tier"], "F (Guaranteed Failure)")
        self.assertTrue(any("Budget Starvation" in d["category"] for d in res["deductions"]))
        self.assertTrue(any("Pixel Poisoning" in d["category"] for d in res["deductions"]))
        self.assertTrue(any("Pangle Placement" in d["category"] for d in res["deductions"]))


class TestSpendMatch(unittest.TestCase):
    def test_below_threshold(self):
        res = evaluate_spend_match(150.0)
        self.assertIsNone(res["matched_tier"])
        self.assertEqual(res["credit_match"], 0.0)
        self.assertEqual(res["total_purchasing_power"], 150.0)
        self.assertEqual(res["gap_to_next_tier"], 50.0)

    def test_tier_1_match(self):
        res = evaluate_spend_match(250.0)
        self.assertEqual(res["matched_tier"]["name"], "Tier 1: Starter")
        self.assertEqual(res["credit_match"], 200.0)
        self.assertEqual(res["total_purchasing_power"], 450.0)

    def test_tier_3_match(self):
        res = evaluate_spend_match(4000.0)
        self.assertEqual(res["matched_tier"]["name"], "Tier 3: Scale (Most Popular)")
        self.assertEqual(res["credit_match"], 3000.0)
        self.assertEqual(res["total_purchasing_power"], 7000.0)

    def test_tier_4_max_cap(self):
        res = evaluate_spend_match(15000.0)
        self.assertEqual(res["matched_tier"]["name"], "Tier 4: Enterprise")
        self.assertEqual(res["credit_match"], 6000.0)
        self.assertEqual(res["total_purchasing_power"], 21000.0)


class TestCliExecution(unittest.TestCase):
    def test_calculate_py_cli(self):
        repo_dir = os.path.dirname(os.path.abspath(__file__))
        out = subprocess.check_output([
            sys.executable,
            "calculate.py" if os.path.exists(os.path.join(repo_dir, "calculate.py")) else "audit.py",
            "--spend" if os.path.exists(os.path.join(repo_dir, "calculate.py")) else "spend-match",
            "4500",
            "--json"
        ], cwd=repo_dir)
        data = json.loads(out)
        self.assertEqual(data["credit_match"], 3000)
        self.assertEqual(data["total_ad_power"], 7500)

    def test_cli_pangle_json(self):
        repo_dir = os.path.dirname(os.path.abspath(__file__))
        out = subprocess.check_output([
            sys.executable,
            "audit.py",
            "pangle",
            "--spend", "500",
            "--tiktok-clicks", "2500",
            "--site-sessions", "2000",
            "--pangle-sessions", "1800",
            "--json"
        ], cwd=repo_dir)
        data = json.loads(out)
        self.assertEqual(data["verdict"], "CRITICAL HIJACK")
        self.assertEqual(data["wasted_spend"], 450.0)

    def test_cli_cold_start_json(self):
        repo_dir = os.path.dirname(os.path.abspath(__file__))
        out = subprocess.check_output([
            sys.executable,
            "audit.py",
            "cold-start",
            "--budget", "300",
            "--target-cpa", "25",
            "--json"
        ], cwd=repo_dir)
        data = json.loads(out)
        self.assertEqual(data["survival_score"], 100)

    def test_cli_spend_match_json(self):
        repo_dir = os.path.dirname(os.path.abspath(__file__))
        out = subprocess.check_output([
            sys.executable,
            "audit.py",
            "spend-match",
            "4000",
            "--json"
        ], cwd=repo_dir)
        data = json.loads(out)
        self.assertEqual(data["credit_match"], 3000.0)


if __name__ == "__main__":
    unittest.main()
