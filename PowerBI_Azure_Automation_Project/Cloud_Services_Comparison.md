# Cloud Service Comparison for Power BI Automation

**Purpose:** This document compares the three major cloud providers (Azure, AWS, GCP) specifically for automating data collection for Power BI Dashboards. Use this table to present to your manager.

---

## 🏆 Executive Summary
For a **Power BI** centric workflow, **Microsoft Azure** is the overwhelming winner.
*   **Why?** It is in the same ecosystem. No "Gateways" needed. Shared security/login.
*   **Cost:** All three are roughly similar (~$5-20/mo for low scale), but Azure is often cheaper for Power BI users because you don't need extra "connector" software.

---

## 📊 Feature & Cost Comparison Table

| Feature | 🟦 Microsoft Azure (Recommended) | 🟧 AWS (Amazon) | 🟥 Google Cloud (GCP) |
| :--- | :--- | :--- | :--- |
| **Power BI Integration** | **Native / Seamless** (Direct Connect) | **Complex** (Requires Gateway) | **Complex** (Requires Gateway) |
| **Data Storage** | Azure SQL Database | AWS RDS (SQL Server/MySQL) | Google Cloud SQL / BigQuery |
| **Automation Tool** | Azure Functions (Python) | AWS Lambda (Python) | Google Cloud Functions (Python) |
| **Data Refresh** | **Cloud-to-Cloud** (No Laptop needed) | **Gateway Required** (Needs VM or Laptop) | **Gateway Required** (Needs VM or Laptop) |
| **Identity/Login** | Uses same Office 365 / Entra ID | Requires separate IAM setup | Requires separate IAM setup |
| **Est. Monthly Cost** (Small Scale) | **~$5 - $15** | **~$15 - $30** | **~$15 - $30** |

---

## 📝 Detailed workflows

### 1. 🟦 Microsoft Azure (The Happy Path)
**Workflow:** `API -> Azure Function -> Azure SQL -> Power BI Service`
*   **How it works:** Power BI Service can talk directly to Azure SQL. They live in the same "Microsoft House".
*   **Pros:**
    *   **No Gateway**: You do NOT need to install software or keep a laptop on.
    *   **Security**: Uses your existing company email/login.
*   **Cons:** You must use Azure Portal (new interface to learn).

### 2. 🟧 Amazon Web Services (AWS)
**Workflow:** `API -> Lambda -> AWS RDS -> [Gateway] -> Power BI Service`
*   **How it works:** AWS stores the data. Power BI tries to reach it, but AWS blocks it by default.
*   **The Problem:** You must install an "On-premise Gateway" on a Windows Virtual Machine (EC2) to act as a bridge.
*   **Hidden Costs:** You have to pay for the Database (RDS) **PLUS** the Windows Virtual Machine (EC2) just to run the Gateway software.
*   **Pros:** Industry standard if your company already puts EVERYTHING in AWS.

### 3. 🟥 Google Cloud Platform (GCP)
**Workflow:** `API -> Cloud Functions -> BigQuery -> Power BI Service`
*   **How it works:** Google BigQuery is excellent for massive data. Power BI has a connector for BigQuery.
*   **Pros:** Good for "Big Data" analytics.
*   **Cons:** Often slower refresh inside Power BI compared to Azure SQL.

---

## 💰 Cost Breakdown (Estimated for Startup Scale)

**Assumptions:** Running script 6 times/day, storing < 1GB of data.

**Azure:**
*   **Function App:** Free (First 1M calls/month are free).
*   **Azure SQL Basic:** ~$5.00 / month.
*   **Total:** **~$5.00 / month**.

**AWS:**
*   **Lambda:** Free (Free tier).
*   **RDS (Database):** ~$15.00 / month (smallest instance).
*   **EC2 (for Gateway):** ~$10.00 / month (t2.micro).
*   **Total:** **~$25.00 / month**.

**GCP:**
*   **Cloud Functions:** Free (Free tier).
*   **Cloud SQL:** ~$10-15 / month.
*   **Total:** **~$15.00 / month**.

---

## 🎯 Recommendation for Manager
"Isolating Power BI automation to **Azure** is the most cost-effective and lowest-maintenance option. Using AWS or GCP introduces a requirement for an 'On-premise Gateway', which adds complexity, points of failure, and cost (VM hosting). Since we are already paying for Power BI (Microsoft), adding Azure SQL is the natural fit."
