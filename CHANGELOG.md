# Changelog & TikTok Policy Tracking 📜

All notable updates, TikTok Ads policy changes, and milestone verification audits are documented in this file.

---

## [2026.05] - Open-Source Anti-Leak & Cold-Start Diagnostic Suite
### Added
* **Pangle Traffic & Budget Leak Detector (`audit.py pangle`)**: Diagnostic engine detecting low-intent bot traffic from third-party gaming apps outside TikTok. Parses live metrics or Shopify/GA4 CSV exports, calculates effective CPC inflation, and provides a 5-step placement remediation protocol.
* **Cold-Start Campaign Survival Linter (`audit.py cold-start`)**: Algorithmic pre-launch auditor scoring campaign setups (0–100) based on 30-day empirical Reddit media buyer failure data (evaluating budget:CPA ratio, pixel poisoning like ATC/traffic, automatic placements, and hook format friction).
* **Empirical Reddit Research Dossier**: Added `research-tiktok-ads-reddit-30days.md` analyzing 64 community threads across `r/TikTokAds`, `r/PPC`, `r/dropship`, and `r/shopify`.
* **Automated Test Suite**: Added `test_audit.py` with 100% pass rate across CLI parsing, financial calculations, and edge cases.

---

## [2026.04] - Enterprise Cap & VCC Fraud Engine Update
### Verified Policy Audit
* **$6,000 Milestone Cap Maintained**: Confirmed Tier 4 matching holds up to $6,000 for verified agency accounts spending ≥$10,000 in net advertising within 30 days.
* **Automated Risk Engine Advisory**: TikTok Ads Manager enhanced its automated fraud engine regarding virtual credit cards (VCCs). Added advisory against unverified prepaid cards; whitelisted agency lines now require direct balance top-ups to prevent automatic learning-phase suspensions.
* **CLI Utility Added**: Introduced `calculate.py` for standalone terminal simulation and automated media-buying pipelines.

---

## [2026.01] - Official Match Structure Harmonization
### Added
* Formalized the 4-tier spend match structure ($200 ➔ $200, $1,000 ➔ $750, $4,000 ➔ $3,000, $10,000 ➔ $6,000).
* Deployed interactive client-side calculator at [adgrowth-lab.github.io](https://adgrowth-lab.github.io/).
* Partner attribution handshake verified with `partnerlinks.io` official gateway.

---

## [2025.10] - Initial Public Audit Release
### Security & Transparency
* Published benchmark analysis exposing secondary broker markups (5%–15% fee extraction).
* Established direct route documentation connecting advertisers directly to TikTok Ads Manager without intermediary escrow accounts.
