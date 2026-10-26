#!/usr/bin/env python3
"""
TikTok Ads Spend Match & Purchasing Power Estimator (2026 Edition)
Standalone zero-dependency simulation CLI for media buyers and advertisers.
Part of the Adgrowth-Lab Open Source Transparency Initiative.
"""

import sys
import argparse
import json

TIERS = [
    {
        "name": "Tier 1: Starter",
        "min_spend": 200,
        "credit_match": 200,
        "ratio_desc": "100% Match (2.0x Purchasing Power)",
        "best_for": "Pixel warm-up & initial product validation"
    },
    {
        "name": "Tier 2: Growth",
        "min_spend": 1000,
        "credit_match": 750,
        "ratio_desc": "75% Match (1.75x Purchasing Power)",
        "best_for": "Validated CBO scaling & retargeting testing"
    },
    {
        "name": "Tier 3: Scale (Most Popular)",
        "min_spend": 4000,
        "credit_match": 3000,
        "ratio_desc": "75% Match (1.75x Purchasing Power)",
        "best_for": "Winning creative scaling & high-volume dropshipping"
    },
    {
        "name": "Tier 4: Enterprise",
        "min_spend": 10000,
        "credit_match": 6000,
        "ratio_desc": "60% Match (Maximum $6,000 Official Cap)",
        "best_for": "Multi-store DTC brands & high-velocity agencies"
    }
]

OFFICIAL_PORTAL = "https://getstartedtiktok.partnerlinks.io/apmgdhnv6eng"
WEB_CALCULATOR = "https://adgrowth-lab.github.io/"


def evaluate_spend(spend: float, currency: str = "USD") -> dict:
    """Evaluate qualifying spend and return tier benefits and ROI multipliers."""
    spend = max(0.0, float(spend))
    matched_tier = None
    next_tier = None

    for i, t in enumerate(TIERS):
        if spend >= t["min_spend"]:
            matched_tier = t
            if i + 1 < len(TIERS):
                next_tier = TIERS[i + 1]
            else:
                next_tier = None
        else:
            if matched_tier is None:
                next_tier = t
            break

    credit = matched_tier["credit_match"] if matched_tier else 0
    total_power = spend + credit
    effective_multiplier = round(total_power / spend, 2) if spend > 0 else 1.0
    cpa_discount_pct = round((credit / total_power) * 100, 1) if total_power > 0 else 0.0

    gap_to_next = 0.0
    if next_tier:
        gap_to_next = round(next_tier["min_spend"] - spend, 2)

    return {
        "spend": spend,
        "currency": currency.upper(),
        "qualifying_tier": matched_tier["name"] if matched_tier else "Below Tier 1 ($200 Min)",
        "credit_match": credit,
        "total_ad_power": total_power,
        "purchasing_multiplier": f"{effective_multiplier}x",
        "effective_cpa_discount": f"{cpa_discount_pct}%",
        "best_for": matched_tier["best_for"] if matched_tier else f"Spend another ${gap_to_next:.2f} to unlock Tier 1 (+$200 free credit)",
        "next_tier_gap": gap_to_next,
        "next_tier_name": next_tier["name"] if next_tier else None,
        "official_partner_route": OFFICIAL_PORTAL,
        "web_calculator": WEB_CALCULATOR
    }


def print_receipt(res: dict):
    """Render a clean, high-authority terminal receipt for media buyers."""
    c = res["currency"]
    s = res["spend"]
    match = res["credit_match"]
    tot = res["total_ad_power"]

    print("\n" + "=" * 62)
    print(" 🎯 TIKTOK ADS SPEND MATCH ESTIMATOR & BENEFIT AUDIT (2026)")
    print("=" * 62)
    print(f" Target Monthly Budget:     {c} ${s:,.2f}")
    print(f" Qualifying Milestone:      {res['qualifying_tier']}")
    print("-" * 62)
    if match > 0:
        print(f" ✅ Promotional Voucher:     +{c} ${match:,.2f} (Direct Ads Manager Match)")
        print(f" 🚀 Total Ad Buying Power:   {c} ${tot:,.2f}")
        print(f" 📈 Purchasing Multiplier:   {res['purchasing_multiplier']} Capital Leverage")
        print(f" 💸 Effective CPA Discount:  ~{res['effective_cpa_discount']} Cost Reduction")
    else:
        print(" ⚠️  Status:                  Below Minimum Threshold ($200.00)")
        print(f" 💡 Advice:                  Spend ${res['next_tier_gap']:,.2f} more to get +$200 credit")
    print("-" * 62)
    print(f" 🎯 Strategic Focus:        {res['best_for']}")

    if res.get("next_tier_name") and match > 0:
        print(f" 💡 Pro Tip:                 Add ${res['next_tier_gap']:,.2f} spend to upgrade to {res['next_tier_name']}")

    print("=" * 62)
    print(f" 🔗 Claim Route:  {res['official_partner_route']}")
    print(f" 🌐 Web Simulator: {res['web_calculator']}")
    print("=" * 62 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="Simulate official TikTok Ads Manager spend milestone matching vouchers."
    )
    parser.add_argument(
        "--spend", "-s",
        type=float,
        help="Planned 30-day net advertising spend (USD)",
        default=None
    )
    parser.add_argument(
        "--currency", "-c",
        type=str,
        help="Billing currency (default: USD)",
        default="USD"
    )
    parser.add_argument(
        "--json", "-j",
        action="store_true",
        help="Output raw JSON results for automated reporting pipelines"
    )

    args = parser.parse_args()

    spend = args.spend
    if spend is None:
        try:
            val = input("Enter your planned 30-day TikTok Ads spend in USD (e.g. 4000): ").strip()
            spend = float(val) if val else 4000.0
        except (ValueError, KeyboardInterrupt):
            print("\nAborted.")
            sys.exit(0)

    result = evaluate_spend(spend, args.currency)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print_receipt(result)


if __name__ == "__main__":
    main()
