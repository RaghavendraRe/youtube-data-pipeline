# Azure Cost Breakdown: What You Actually Pay For

You asked: *"Is there an entire payment for Azure or selected service only?"*
**Answer:** You **ONLY** pay for the specific services you select. There is no "entrance fee" for Azure.

---

## 🛒 The "Shopping List" for this Pipeline

To build the dashboard pipeline (`API -> Python -> SQL -> Power BI`), you need exactly **3 things**. Here is the price tag for each:

| Item Name | Service Type | Estimated Cost (Monthly) | Notes |
| :--- | :--- | :--- | :--- |
| **1. Azure Functions** | Compute (Running the Script) | **$0.00** (Free) | The first 1 million calls per month are free. Your script runs ~180 times/month (6x/day). You pay nothing. |
| **2. Azure SQL Database** | Storage (Saving Data) | **~$5.00** (₹420) | Select "Basic Tier" (2GB storage). This is enough for 5+ years of YouTube data. |
| **3. Power BI Pro** | Visualization License | **~$10.00** (₹830) / user | You likely already have this license if you use Power BI at work. |

### 🏷️ Total Monthly Bill: **~$15.00 (Approx ₹1,250)**
*(If you already have Power BI licenses, the extra cost is only **~$5.00** for the database).*

---

## 💳 How the Payment Works

1.  **Subscription Model:** You sign up for a "Pay-As-You-Go" subscription.
2.  **Credit Card:** You link a corporate credit/debit card.
3.  **Billing:** At the end of the month, Microsoft calculates usage.
    *   Did you use a Virtual Machine? **No.** (Cost: $0)
    *   Did you use AI services? **No.** (Cost: $0)
    *   Did you use SQL Database? **Yes.** (Cost: $5)
    *   **Final Bill:** $5.

### ⚠️ Important Manager Note: "Budget Cap"
To prevent accidental overspending, we can set a **Budget Alert** in Azure.
*   *Settings:* "Email me if bill goes over $20".
*   This removes the fear of a "surprise bill".

---

## 📝 What to tell your Manager

*"We do not need to buy 'All of Azure'. We only 'rent' two specific tiny services:*
1.  *A place to store data (SQL DB) for ~$5/month.*
2.  *A script runner (Functions) which is effectively free.*

*This is a micro-cost architecture, not an enterprise deployment."*
