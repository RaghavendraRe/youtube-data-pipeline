# Get Data - Web Method Guide

## 📌 Overview
This is the **simplest UI-based approach** to get YouTube data into Power BI without writing any code.

---

## 🚀 Method 3: Get Data > Web

### Step 1: Get Data from Web
1. Open Power BI Desktop
2. Click **Home** > **Get Data** > **Web**

### Step 2: Enter the API URL

**For Channel Info:**
```
https://www.googleapis.com/youtube/v3/channels?key=AIzaSyBM5DU838aPORBzQE7L3Hv1q7PGSEQlGU&id=UCUDKhNE_Y_DVkFx1nFNZTWQ&part=contentDetails,statistics
```

Click **OK**

### Step 3: Navigate the JSON Response
1. Power BI will show **Navigator** window
2. You'll see a hierarchical view of the JSON
3. Click on **items** > **List**
4. Click **Transform Data**

### Step 4: Expand the Data
1. In Power Query Editor, click the **expand button** (two arrows) on the column
2. Select the fields you want:
   - `contentDetails` → `relatedPlaylists` → `uploads`
   - `statistics` → `subscriberCount`, `viewCount`, `videoCount`

### Step 5: Get Videos from Uploads Playlist

Now you need the uploads playlist ID from Step 4. Let's say it's: `UUUDKhNE_Y_DVkFx1nFNZTWQ`

**Create New Query:**
1. Home > New Source > Web
2. Enter URL:
```
https://www.googleapis.com/youtube/v3/playlistItems?key=AIzaSyBM5DU838aPORBzQE7L3Hv1q7PGSEQlGU&playlistId=UUUDKhNE_Y_DVkFx1nFNZTWQ&part=snippet,contentDetails&maxResults=50
```

3. Click Transform Data
4. Expand **items**
5. Expand **snippet** and **contentDetails** to get:
   - `publishedAt`
   - `videoId`
   - `title`

### Step 6: Get Video Details

**Create Another Query:**
1. Home > New Source > Web
2. You need to create a URL with video IDs from Step 5
3. Example URL (replace VIDEO_IDS with actual IDs separated by commas):
```
https://www.googleapis.com/youtube/v3/videos?key=AIzaSyBM5DU838aPORBzQE7L3Hv1q7PGSEQlGU&id=VIDEO_ID_1,VIDEO_ID_2,VIDEO_ID_3&part=snippet,contentDetails,statistics
```

4. Expand **items**
5. Expand all nested fields:
   - `snippet` → title, description, tags, publishedAt
   - `contentDetails` → duration
   - `statistics` → viewCount, likeCount, commentCount

### Step 7: Add Custom Columns

In Power Query, add calculated columns:

**Duration in Seconds:**
1. Add Column > Custom Column
2. Formula (simplified - you may need to adjust):
```m
if Text.Contains([duration], "H") then
    Number.FromText(Text.BetweenDelimiters([duration], "PT", "H")) * 3600
else if Text.Contains([duration], "M") then
    Number.FromText(Text.BetweenDelimiters([duration], "PT", "M")) * 60
else
    Number.FromText(Text.BetweenDelimiters([duration], "PT", "S"))
```

**Engagement:**
```m
[likeCount] + [commentCount]
```

**Engagement Rate:**
```m
if [viewCount] > 0 then ([likeCount] + [commentCount]) / [viewCount] else 0
```

**Video Type:**
```m
if [durationSeconds] <= 60 then "Short" else "Long"
```

### Step 8: Handle Pagination

⚠️ **Important Limitation:**
- The Web method only fetches one page (max 50 items)
- To get more videos, you need to:
  1. Check for `nextPageToken` in the JSON response
  2. Create additional queries with `&pageToken=NEXT_TOKEN`
  3. Append all queries together

This gets complex quickly, which is why **Method 2 (Advanced Editor)** is better for large datasets!

### Step 9: Close & Apply

Once you have all your transformations:
1. Click **Close & Apply**
2. Data loads into Power BI

---

## ✅ Pros of This Method

- **No coding required** - Pure UI clicks
- **Visual** - See the data structure as you build
- **Good for learning** - Understand JSON structure
- **Great for small datasets** - Single page of results

## ❌ Cons of This Method

- **Manual pagination** - Can't easily fetch all videos
- **Repetitive** - Need to create multiple queries
- **Limited logic** - Complex calculations are harder
- **Not scalable** - For 2 years of data, this becomes tedious

---

## 🎯 Recommendation

**Use This Method When:**
- You only need the latest 50 videos
- You want to explore the API structure
- You're learning Power Query

**Use Method 2 (Advanced Editor) When:**
- You need ALL videos from 2 years
- You want playlist mapping
- You need complex calculations
- You want automated pagination

---

## 📝 Summary

| Feature | Get Data - Web | Advanced Editor |
|---------|---------------|----------------|
| Ease of Use | ⭐⭐⭐⭐⭐ Very Easy | ⭐⭐⭐ Moderate |
| Scalability | ⭐⭐ Limited | ⭐⭐⭐⭐⭐ Excellent |
| Pagination | ❌ Manual | ✅ Automatic |
| Calculations | ⭐⭐ Basic | ⭐⭐⭐⭐⭐ Advanced |
| Best For | Learning/Small data | Production/All data |
