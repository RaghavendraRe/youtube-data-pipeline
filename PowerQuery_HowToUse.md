# Power Query Advanced Editor - Step-by-Step Guide

## 📌 Overview
This guide shows you how to use the Power Query M code to fetch YouTube data directly in Power BI Desktop.

---

## 🚀 How to Use This Code

### Step 1: Open Power BI Desktop

### Step 2: Get Data > Blank Query
1. Click **Home** tab
2. Click **Get Data** dropdown
3. Select **Blank Query**

### Step 3: Open Advanced Editor
1. In Power Query window, click **View** tab
2. Click **Advanced Editor** button

### Step 4: Paste the Code
1. Delete any existing code in the editor
2. Open the file: `YouTube_PowerQuery_AdvancedEditor.pq`
3. Copy ALL the code
4. Paste it into the Advanced Editor

### Step 5: Click Done
- Power BI will start fetching data
- This may take 2-5 minutes depending on the number of videos

### Step 6: Review the Data
- You should see all columns matching your Python script output
- Check the column names and data types

### Step 7: Rename the Query (Optional)
1. Right-click the query name (usually "Query1")
2. Rename to something like: `YouTube_BrahmaKumaris_Videos`

### Step 8: Close & Apply
- Click **Close & Apply** to load data into Power BI

---

## ⚠️ Important Notes

### API Key Security
- The API key is hardcoded in line 6
- For production, use Power BI Parameters instead:
  1. Home > Manage Parameters > New Parameter
  2. Name: `YouTubeAPIKey`
  3. Type: Text
  4. Replace line 6 with: `API_KEY = YouTubeAPIKey`

### Performance
- Fetching 2 years of data may take time
- The script uses batches of 50 videos for efficiency
- First run will be slower; subsequent refreshes use the same logic

### Troubleshooting

**Error: "DataSource.Error"**
- Check your internet connection
- Verify the API key is valid
- Check YouTube API quota limits

**Error: "Expression.Error"**
- Make sure you copied the ENTIRE code
- Check for any missing brackets or quotes

**No data showing**
- Check if there are videos in the last 2 years
- Verify the Channel ID is correct

---

## 📊 Expected Output Columns

The final table will have these columns (matching your Python script):

1. Video ID
2. Video URL
3. Title
4. Description
5. Published Date
6. Duration (Sec)
7. Duration (ISO)
8. Is Short
9. Is Live
10. Video Type
11. Views
12. Likes
13. Comments
14. Engagement
15. Engagement Rate
16. Tags
17. All Playlists
18. Podcast Name
19. Category ID
20. Channel Title
21. Definition (HD/SD)
22. Live Start
23. Live End
24. First Fetched At
25. Last Fetched At

---

## 🎯 Next Steps

After loading the data:
1. Create relationships (if needed)
2. Build your visualizations
3. Set up scheduled refresh (Power BI Service)

---

## 💡 Tips

- **Refresh**: Click Refresh in Power BI to update data
- **Filter**: Add filters in Power Query if you want to limit data
- **Modify**: You can edit the code to change date ranges or add more metrics
