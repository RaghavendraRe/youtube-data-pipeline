# GitHub Actions# YouTube Data Pipeline (Multi-Channel Edition)

This project automates the data collection for **39+ Brahma Kumaris YouTube Channels**, organizing them by "Wing" and "Entity Name" for Power BI reporting.

## 🚀 Features (Phase 1 Complete)
- **Multi-Channel Support**: dynamically reads channel list from `data/handles_list.xlsx`.
- **Full History**: Fetches up to 100 years of video history.
- **Smart Schema**:
    - **Fact Table**: `data/brahmakumaris_videos.csv` (86,000+ rows) - Granular video metrics.
    - **Dimension Table**: `data/channel_summary_audit.csv` - Channel-level stats (Subscribers, Wings).
- **Optimized**: Fast execution (~10 mins) with reduced API usage.

## 📂 Project Structure
```
├── fetch_youtube_data.py   # Main ETL script (fetches videos)
├── fetch_channel_audit.py  # Audit script (fetches subs/channel stats)
├── config.yaml             # Configuration (API keys, settings)
├── requirements.txt        # Python dependencies
├── data/
│   ├── brahmakumaris_videos.csv  # The BIG data file
│   ├── channel_summary_audit.csv # Channel Master list
│   └── handles_list.xlsx         # Input list of channels
└── utils/
    └── handle_parser.py    # Helper to read Excel inputs
```

## 🛠️ Setup
1.  **Clone the Repo**:
    ```bash
    git clone <repo-url>
    ```
2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
3.  **Configure**:
    - Add your `YOUTUBE_API_KEY` to `.env` file.
    - Ensure `data/handles_list.xlsx` is present.

## 🏃‍♂️ Usage
**To collect all video data:**
```bash
python fetch_youtube_data.py
```
**To valid/audit channel list:**
```bash
python fetch_channel_audit.py
```

## 📊 Power BI Instructions
1.  Import both CSV files from `data/`.
2.  Link them using **Channel ID**.
3.  Use "Wing" and "Entity Name" as Slicers.  A["🕒 Scheduled Daily (00:00 UTC)"] -->|Trigger| B("GitHub Actions Runner")
    B -->|Setup| C{"Python Environment"}
    C -->|Install| D["Dependencies"]
    D -->|Run Script| E["fetch_youtube_data.py"]
    
    E -->|Request Data| F(("YouTube Data API"))
    F -->|Return JSON| E
    
    E -->|Process & Transform| G[/"brahmakumaris_videos.csv"/]
    G -->|Commit & Push| H["GitHub Repository"]
    
    H -->|Raw URL Connection| I["Power BI Dashboard"]
    I -->|Scheduled Refresh| J["Auto-Updated Reports"]

    style A fill:#f9f,stroke:#333
    style F fill:#ff0000,stroke:#333,color:white
    style I fill:#f2c811,stroke:#333
```

## �🚀 Quick Start

### 1️⃣ Initialize GitHub Repository

```bash
# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit: YouTube ETL pipeline"

# Create GitHub repo and push
# Option A: Using GitHub CLI
gh repo create my-youtube-pipeline --public --source=. --remote=origin --push

# Option B: Manual (create repo on GitHub.com first, then)
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
git branch -M main
git push -u origin main
```

### 2️⃣ Set Up GitHub Secrets

1. Go to your GitHub repository
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add these secrets:

| Secret Name | Value | Description |
|------------|-------|-------------|
| `YOUTUBE_API_KEY` | Your YouTube API key | Get from [Google Cloud Console](https://console.cloud.google.com/) |
| `YOUTUBE_CHANNEL_ID` | `UCUDKhNE_Y_DVkFx1nFNZTWQ` | Brahmakumaris channel ID |

### 3️⃣ Enable GitHub Actions

1. Go to **Actions** tab in your repository
2. If prompted, click **"I understand my workflows, go ahead and enable them"**
3. You should see the workflow **"YouTube Data Collection ETL"**

### 4️⃣ Test the Workflow

**Manual Test:**
1. Go to **Actions** tab
2. Click **YouTube Data Collection ETL**
3. Click **Run workflow** → **Run workflow**
4. Watch it execute (takes ~2-5 minutes)
5. Check the `data/` directory for updated CSV

**Automatic Schedule:**
- Runs daily at **12:00 AM UTC** (5:30 AM IST)
- Automatically commits updated data to the repository

## 📊 Connecting to Power BI

### Method 1: Direct GitHub URL (Recommended)

1. Open Power BI Desktop
2. **Get Data** → **Web**
3. Use the raw GitHub URL:
   ```
   https://raw.githubusercontent.com/YOUR_USERNAME/YOUR_REPO/main/data/brahmakumaris_videos.csv
   ```
4. Click **OK** → **Load**
5. Set up **Scheduled Refresh** in Power BI Service

### Method 2: Clone Repository Locally

1. Clone the repository:
   ```bash
   git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git
   ```
2. In Power BI Desktop
   **Get Data** → **Text/CSV**
3. Browse to `data/brahmakumaris_videos.csv`
4. Pull latest data with `git pull` before refreshing

### Method 3: Power BI Service (Premium)

For automatic refresh in Power BI Premium:

1. Publish your report to Power BI Service
2. Go to **Dataset settings**
3. **Scheduled refresh** → **Add another time**
4. Set to refresh after GitHub Actions runs (e.g., 1:00 AM UTC)

## 🔧 Configuration

### Modify Schedule

Edit [`.github/workflows/youtube-etl.yml`](.github/workflows/youtube-etl.yml):

```yaml
on:
  schedule:
    - cron: '0 0 * * *'  # Daily at midnight UTC
    # Examples:
    # - cron: '0 */6 * * *'  # Every 6 hours
    # - cron: '0 0 * * 0'    # Weekly on Sunday
    # - cron: '0 12 * * *'   # Daily at noon UTC
```

### Modify Data Collection

Edit [`config.yaml`](config.yaml) to change:
- Days of history to collect
- Official podcast names
- Output fields

## 📈 Monitoring

### View Run History
1. Go to **Actions** tab
2. Click on any workflow run
3. View logs, artifacts, and job summary

### Download Data Manually
1. Go to **Actions** tab → Select a workflow run
2. Scroll to **Artifacts**
3. Download `youtube-data-XXX.zip`

### Check for Errors
- Workflow sends status in job summary
- Failed runs will show red X
- Click on failed run to see error logs

## 💰 Cost

| Component | Cost |
|-----------|------|
| GitHub Actions | **Free** (2,000 min/month) |
| GitHub Storage | **Free** (1 GB) |
| YouTube API | **Free** (10,000 units/day) |
| **Total** | **$0/month** |

## 🔒 Security Notes

- ✅ API keys stored in GitHub Secrets (encrypted)
- ✅ Never commit API keys to repository
- ✅ Workflow runs in isolated environment
- ✅ Data commits use GitHub Actions bot account

## 🐛 Troubleshooting

### Workflow not running
- Check if GitHub Actions is enabled
- Verify cron syntax
- Check repository permissions

### API errors
- Verify `YOUTUBE_API_KEY` secret is set correctly
- Check API quota in Google Cloud Console
- Ensure API key has YouTube Data API v3 enabled

### No data updates
- Check workflow run logs for errors
- Verify CSV file is being committed
- Ensure no file size limits exceeded

## 📚 Next Steps

After this method is working:
- [ ] Set up Power BI dashboard
- [ ] Configure scheduled refresh
- [ ] Explore **n8n workflow** alternative
- [ ] Add more data sources (Instagram, Facebook)

## 🔗 Useful Links

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [YouTube Data API](https://developers.google.com/youtube/v3)
- [Power BI Web Connector](https://learn.microsoft.com/en-us/power-bi/connect-data/desktop-connect-to-web)
- [Cron Expression Generator](https://crontab.guru/)
