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
    audit_creative_compliance,
    evaluate_vcc_bin,
    generate_appeal,
    run_comprehensive_defense_suite,
    TIERS,
    VCC_BIN_DATABASE,
    APPEAL_CATALOG
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

    def test_cli_compliance_json(self):
        repo_dir = os.path.dirname(os.path.abspath(__file__))
        out = subprocess.check_output([
            sys.executable,
            "audit.py",
            "compliance",
            "--text", "Natural soothing botanical moisture for daily skincare.",
            "--json"
        ], cwd=repo_dir)
        data = json.loads(out)
        self.assertEqual(data["compliance_score"], 100)
        self.assertEqual(data["risk_tier"], "CLEAN")

    def test_cli_bin_json(self):
        repo_dir = os.path.dirname(os.path.abspath(__file__))
        out = subprocess.check_output([
            sys.executable,
            "audit.py",
            "bin",
            "405081",
            "--json"
        ], cwd=repo_dir)
        data = json.loads(out)
        self.assertEqual(data["risk_tier"], "LOW")
        self.assertEqual(data["issuer"], "Mercury (Choice Financial Group)")

    def test_cli_appeal_json(self):
        repo_dir = os.path.dirname(os.path.abspath(__file__))
        out = subprocess.check_output([
            sys.executable,
            "audit.py",
            "appeal",
            "--type", "payment",
            "--brand", "Test Brand",
            "--account-id", "ADV-9999",
            "--json"
        ], cwd=repo_dir)
        data = json.loads(out)
        self.assertIn("Test Brand", data["subject"])
        self.assertIn("ADV-9999", data["body"])

    def test_cli_full_audit_json(self):
        repo_dir = os.path.dirname(os.path.abspath(__file__))
        out = subprocess.check_output([
            sys.executable,
            "audit.py",
            "full-audit",
            "--budget", "200",
            "--target-cpa", "20",
            "--bin", "405081",
            "--ad-text", "Hydrating plant-based body wash.",
            "--json"
        ], cwd=repo_dir)
        data = json.loads(out)
        self.assertGreaterEqual(data["composite_safety_score"], 90)
        self.assertIn("GREEN LIGHT", data["verdict"])


class TestCreativeCompliance(unittest.TestCase):
    def test_clean_copy_passes(self):
        res = audit_creative_compliance("Discover our refreshing morning hydration routine. Formulated with green tea extract.")
        self.assertEqual(res["compliance_score"], 100)
        self.assertEqual(res["risk_tier"], "CLEAN")
        self.assertEqual(res["critical_violations"], 0)

    def test_critical_exaggeration_and_body_shaming(self):
        res = audit_creative_compliance("Get 100% cure for belly fat and lose 15 lbs in 3 days!")
        self.assertLess(res["compliance_score"], 50)
        self.assertIn(res["risk_tier"], ("HIGH", "CRITICAL"))
        self.assertGreaterEqual(res["critical_violations"], 2)
        flagged_categories = [v["category"] for v in res["violations"]]
        self.assertTrue(any("Absolute Superlatives" in c for c in flagged_categories))
        self.assertTrue(any("Weight Loss" in c for c in flagged_categories))

    def test_counterfeit_ip_violation(self):
        res = audit_creative_compliance("Selling 1:1 replica designer dupe sneakers for cheap!")
        self.assertLessEqual(res["compliance_score"], 60)
        self.assertTrue(any("Counterfeit" in v["category"] for v in res["violations"]))

    def test_get_rich_quick_violation(self):
        res = audit_creative_compliance("Learn the passive income secret to get rich quick and make money while you sleep!")
        self.assertLess(res["compliance_score"], 70)
        self.assertTrue(any("Deceptive Financial" in v["category"] for v in res["violations"]))


class TestVccBinEvaluator(unittest.TestCase):
    def test_mercury_bin_low_risk(self):
        res = evaluate_vcc_bin("405081")
        self.assertTrue(res["recognized"])
        self.assertEqual(res["risk_tier"], "LOW")
        self.assertAlmostEqual(res["pass_rate_pct"], 96.0)
        self.assertTrue(res["supports_3ds"])
        self.assertIn("Mercury", res["issuer"])

    def test_stripe_bin_low_risk(self):
        res = evaluate_vcc_bin("414328")
        self.assertTrue(res["recognized"])
        self.assertEqual(res["risk_tier"], "LOW")
        self.assertIn("Stripe", res["issuer"])

    def test_capitalist_bin_critical(self):
        res = evaluate_vcc_bin("486555")
        self.assertTrue(res["recognized"])
        self.assertEqual(res["risk_tier"], "CRITICAL")
        self.assertFalse(res["supports_3ds"])

    def test_unindexed_bin_fallback(self):
        res = evaluate_vcc_bin("499999")
        self.assertFalse(res["recognized"])
        self.assertEqual(res["brand"], "Visa")
        self.assertIn("anti_ban_checklist", res)
        self.assertEqual(len(res["anti_ban_checklist"]), 5)


class TestAppealGenerator(unittest.TestCase):
    def test_unusual_activity_appeal(self):
        res = generate_appeal(
            appeal_type="unusual-activity",
            brand="Peak Alpha LLC",
            account_id="ADV-112233",
            website="peakalpha.io"
        )
        self.assertIn("Peak Alpha LLC", res["subject"])
        self.assertIn("ADV-112233", res["body"])
        self.assertIn("peakalpha.io", res["body"])
        self.assertEqual(len(res["required_documents"]), 4)

    def test_payment_appeal(self):
        res = generate_appeal(
            appeal_type="payment",
            brand="Nova Commerce",
            account_id="ADV-445566"
        )
        self.assertEqual(res["appeal_type"], "payment")
        self.assertIn("PAYMENT VERIFICATION APPEAL", res["subject"])
        self.assertIn("Nova Commerce", res["body"])

    def test_save_to_file(self):
        with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
            temp_path = f.name

        try:
            res = generate_appeal(
                appeal_type="creative",
                brand="Glow Beauty",
                output_path=temp_path
            )
            self.assertEqual(res["saved_file"], temp_path)
            with open(temp_path, "r", encoding="utf-8") as f:
                content = f.read()
            self.assertIn("Glow Beauty", content)
            self.assertIn("SUBJECT:", content)
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)


class TestComprehensiveDefenseSuite(unittest.TestCase):
    def test_full_suite_clean(self):
        res = run_comprehensive_defense_suite(
            daily_budget=250.0,
            target_cpa=25.0,
            objective="purchase",
            placement="tiktok_only",
            format_type="spark_ads",
            hook_type="creator_face_direct",
            sound="voiceover_trending",
            ad_text="Organic botanical tea for gentle morning hydration.",
            bin_number="405081"
        )
        self.assertGreaterEqual(res["composite_safety_score"], 90.0)
        self.assertIn("GREEN LIGHT", res["verdict"])
        self.assertEqual(res["risk_level"], "LOW RISK")
        self.assertEqual(res["pillar_scores"]["creative_compliance"], 100)
        self.assertEqual(res["pillar_scores"]["campaign_cold_start"], 100)

    def test_full_suite_critical_flaws(self):
        res = run_comprehensive_defense_suite(
            daily_budget=15.0,
            target_cpa=30.0,
            objective="atc",
            placement="automatic",
            format_type="dark_post",
            hook_type="product_static",
            sound="muted",
            ad_text="100% cure for belly fat!",
            bin_number="486555"
        )
        self.assertLess(res["composite_safety_score"], 40.0)
        self.assertIn("RED LIGHT", res["verdict"])
        self.assertEqual(res["fallback_appeal_type"], "creative")
        self.assertGreater(len(res["priority_action_plan"]), 3)


if __name__ == "__main__":
    unittest.main()
