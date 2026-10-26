# TikTok Ads Account Suspension Appeal Field Kit 📨

> **5 battle-tested, high-converting appeal templates and escalation protocols for overturning TikTok Ads Manager and Business Center suspensions.**  
> Built from dozens of successful reinstatements across e-commerce brands, agencies, and dropshippers.

---

## ⚡ The Four-Pillar Evidence Protocol

Over 90% of account appeals are automatically rejected because advertisers write short, emotional complaints (*"I did nothing wrong, please unban my account"*). TikTok's tier-1 support uses automated rejection macros for vague submissions.

To successfully overturn a ban, your ticket must follow the **Four-Pillar Evidence Protocol**:

```
┌────────────────────────────────────────────────────────────────────────┐
│                      THE 4-PILLAR APPEAL ARCHITECTURE                  │
├────────────────────────────────────────────────────────────────────────┤
│ 1. Entity Legitimacy     │ Legal company registration, corporate       │
│    & Identity Proof      │ address, and official domain verification   │
├──────────────────────────┼─────────────────────────────────────────────┤
│ 2. Root-Cause Self-Audit │ Clear, objective explanation of what        │
│                          │ triggered the algorithmic risk flag         │
├──────────────────────────┼─────────────────────────────────────────────┤
│ 3. Remediation & Platform│ Immediate corrective actions already taken  │
│    Alignment             │ (deleted creatives, updated billing AVS)    │
├──────────────────────────┼─────────────────────────────────────────────┤
│ 4. Commercial Commitment │ Long-term planned advertising spend and     │
│    & Human Escalation    │ request for senior risk specialist review   │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 📁 Template Directory & Use Cases

| File | Primary Suspension Reason | Key Evidence Required |
| :--- | :--- | :--- |
| **[`01-unusual-activity-suspension.md`](01-unusual-activity-suspension.md)** | Sudden IP/VPN change, new device, rapid campaign scaling | Business License, Director ID, IP history |
| **[`02-payment-discrepancy-card-verification.md`](02-payment-discrepancy-card-verification.md)** | VCC binding, 3DS authentication failure, billing name mismatch | Bank Statement (last 30d), Card photo (redacted) |
| **[`03-creative-policy-misleading-ad-reversal.md`](03-creative-policy-misleading-ad-reversal.md)** | Policy 5.1/5.2 ad disapproval leading to account disablement | Revised video, lab test certs, refund policy |
| **[`04-business-center-agency-account-ban.md`](04-business-center-agency-account-ban.md)** | Master Business Center (BC) freeze or agency portfolio ban | Agency contracts, sub-account audit, good standing |
| **[`05-identity-business-verification-appeal.md`](05-identity-business-verification-appeal.md)** | Failed Advertiser Identity Verification (KYB/KYC) | IRS EIN letter / VAT doc, Certificate of Inc |

---

## 🛠️ CLI Quick Generator

Generate customized, ready-to-copy appeal letters with pre-filled brand parameters using `audit.py`:

```bash
# 1. Payment Verification Appeal
python3 audit.py appeal --type payment --brand "EcoNest Goods" --account-id "ADV-883921" --output payment_appeal.txt

# 2. Creative Policy Reversal Appeal
python3 audit.py appeal --type creative --brand "Aura Skincare" --account-id "ADV-124992" --website "auraskin.com"

# 3. Unusual Activity Appeal
python3 audit.py appeal --type unusual-activity --brand "Pulse Footwear" --account-id "ADV-554102"
```

---

## 🚨 Document Redaction & Submission Standards

When attaching bank statements or credit card photos:
* **The 4-Digit Rule**: Always redact (black out) the first 12 digits of the credit card number. Show only the **Last 4 Digits** and the **Cardholder Name**.
* **Financial Privacy**: You may redact transaction amounts unrelated to TikTok Ads on bank statements, but **keep TikTok authorization lines, the bank header, and company address fully visible**.
* **File Format**: Always combine all documents into a single, clean multi-page PDF named `[BrandName]_TikTok_Verification_Documents.pdf`.

---

## 🧭 Step-by-Step Escalation Protocol

1. **Submit Tier-1 Ticket**:
   * Navigate to: **TikTok Ads Manager ➔ '?' Support Icon (top right) ➔ Customer Support ➔ Account Review / Appeal**.
   * Paste the customized template and attach your verification PDF.
2. **24-Hour Rule**:
   * If no human response within 24 hours, click the **Live Chat** icon during peak business hours (09:00–18:00 UTC).
   * Provide your Ticket ID and say: *"We have uploaded our complete corporate verification packet and bank statements under Ticket #[ID]. Could you kindly escalate this to a Tier-2 Risk Specialist for expedited review?"*
3. **NEVER Churn and Burn**:
   * Do not immediately open a new ad account with the same domain name or credit card while an appeal is open. This will link the accounts and cause permanent hardware/domain blacklisting.
