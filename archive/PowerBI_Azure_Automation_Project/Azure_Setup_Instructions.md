# Azure Setup Instructions for Power BI Automation

Follow these steps in the [Azure Portal](https://portal.azure.com) to prepare your environment.

## 1. Create a Resource Group
*   Search for "Resource groups" in the top bar and click **Create**.
*   **Name**: `PowerBIFocusGroup` (or similar).
*   **Region**: Select a region close to you (e.g., "East US" or your local region).
*   Click **Review + create** -> **Create**.

## 2. Create an Azure SQL Database
*   Search for "SQL databases" and click **Create**.
*   **Resource Group**: Select the `PowerBIFocusGroup` you just created.
*   **Database name**: e.g., `YoutubeDataDB`.
*   **Server**: Click "Create new".
    *   **Server name**: Give it a unique name.
    *   **Authentication**: Use "Use SQL authentication".
    *   **Admin login/Password**: Create a username and password. **(IMPORTANT: Save these credentials!)**
*   **Compute + storage**: Click "Configure database".
    *   Select **"Basic"** (cheapest option ~5 USD/mo) or **"Serverless"**.
    *   Click "Apply".
*   Click **Review + create** -> **Create**.

## 3. Allow Your IP Address & Azure Services
*   Go to your new **SQL Database** resource.
*   Click **"Set server firewall"** (in the top menu bar).
*   **Allow Local Access**: Click **"Add your client IPv4 address"** (this allows your computer to connect for testing).
*   **Allow Azure Access**: Check the box **"Allow Azure services and resources to access this server"** (this allows your future Python script to connect).
*   Click **Save**.

## 4. Create a Function App
*   Search for "Function App" and click **Create**.
*   **Resource Group**: Select `PowerBIFocusGroup`.
*   **Name**: Unique name (e.g., `FocusDataCollector`).
*   **Runtime stack**: Select **Python**.
*   **Version**: Select **3.10** or **3.11**.
*   **Hosting**: Select **Consumption** (Pay-as-you-go).
*   Click **Review + create** -> **Create**.

---
**Next Steps:**
Once these are created, we will proceed to:
1.  Get the connection string from the Azure SQL Database.
2.  Modify your Python script to run on the Function App.
