# Method 3: Get Data - Web (UI Approach)

## 📌 Overview
This is the **easiest, no-code method** to get YouTube data into Power BI using only the UI.

**Best for:** Learning, small datasets, quick tests  
**Limitation:** Manual pagination (50 videos per query)

---

## 🚀 Step-by-Step Guide

### **Step 1: Get Data from Web**

1. Open **Power BI Desktop**
2. Click **Home** > **Get Data** > **Web**
3. A dialog will appear

---

### **Step 2: Enter Your First API URL**

**Get Channel Info:**

Paste this URL into the dialog:
```
https://www.googleapis.com/youtube/v3/channels?key=AIzaSyBM5DU838aPORBzQE7L3Hv1q7PVGSEQlGU&id=UCUDKhNE_Y_DVkFx1nFNZTWQ&part=contentDetails,statistics
```

Click **OK**

---

### **Step 3: Navigate the JSON**

Power BI will show the **Navigator** window with JSON data:

1. You'll see: `List`, `Record`, etc.
2. Click on **items** → You'll see a **List** value
3. Click **"List"** → Click **Transform Data**

---

### **Step 4: Expand the Data**

In Power Query Editor:

1. Click the **double-arrow icon** (⬅️➡️) to expand columns
2. Select these fields:
   - ✅ `contentDetails`
   - ✅ `statistics`
3. Click **OK**

4. Expand `contentDetails` again:
   - ✅ `relatedPlaylists` → `uploads`

5. You now have the **Uploads Playlist ID**!

---

### **Step 5: Get Videos from Uploads Playlist**

**Note the Uploads ID** from Step 4 (e.g., `UUUDKhNE_Y_DVkFx1nFNZTWQ`)

1. **Home** > **New Source** > **Web**
2. Paste this URL (replace `UPLOADS_ID` with your actual ID):

```
https://www.googleapis.com/youtube/v3/playlistItems?key=AIzaSyBM5DU838aPORBzQE7L3Hv1q7PVGSEQlGU&playlistId=UPLOADS_ID&part=snippet,contentDetails&maxResults=50
```

3. Click **OK** > **Transform Data**

---

### **Step 6: Expand Video Data**

1. Expand **items** (List)
2. Expand **contentDetails** → Select `videoId`
3. Expand **snippet** → Select `publishedAt`, `title`

You now have a list of **50 video IDs**!

---

### **Step 7: Get Video Details**

For each video, you need details. Here's the challenge:

**Option A: Manual (One Video)**
1. New Source > Web
2. URL:
```
https://www.googleapis.com/youtube/v3/videos?key=AIzaSyBM5DU838aPORBzQE7L3Hv1q7PVGSEQlGU&id=VIDEO_ID&part=snippet,statistics,contentDetails
```
3. Expand: `statistics` (views, likes, comments), `contentDetails` (duration)

**Option B: Function (Advanced - Multiple Videos)**
This requires creating a Power Query function - similar to your working code!

---

### **Step 8: Add Custom Columns**

To calculate metrics:

1. **Add Column** > **Custom Column**
2. Name: `Engagement`
3. Formula: `[likeCount] + [commentCount]`

Repeat for:
- **Engagement Rate**: `[Engagement] / [viewCount]`
- **Video URL**: `"https://www.youtube.com/watch?v=" & [videoId]`

---

### **Step 9: Handle Pagination (Manual)**

⚠️ **Problem:** Web method only fetches 50 videos at a time!

To get more:
1. Check the JSON for `nextPageToken`
2. Create **another Web query** with:
```
https://www.googleapis.com/youtube/v3/playlistItems?key=...&playlistId=...&maxResults=50&pageToken=NEXT_TOKEN
```
3. **Append Queries** to combine them

This becomes tedious for 2 years of data (potentially 2500 videos)!

---

## ✅ Pros of This Method

- ✅ **No coding** - Pure point-and-click
- ✅ **Visual** - See JSON structure as you work
- ✅ **Great for learning** - Understand API responses
- ✅ **Quick setup** - Good for testing API

---

## ❌ Cons of This Method

- ❌ **Limited to 50 results** - Manual pagination needed
- ❌ **Repetitive** - Need many queries for full dataset
- ❌ **No playlist mapping** - Very difficult to implement
- ❌ **Not scalable** - 2 years of data = too many manual steps
- ❌ **Time consuming** - Much slower than Methods 1 & 2

---

## 💡 Comparison with Other Methods

| Feature | Get Data - Web | Power Query Code | Python |
|---------|---------------|------------------|--------|
| Setup Time | ⭐⭐⭐⭐⭐ Fast | ⭐⭐⭐ Medium | ⭐⭐ Slow |
| Coding Required | ❌ None | ✅ M Code | ✅ Python |
| Full Dataset | ❌ No | ✅ Yes | ✅ Yes |
| Pagination | ⚠️ Manual | ✅ Auto | ✅ Auto |
| Playlist Mapping | ❌ Very Hard | ❌ Complex | ✅ Yes |
| Best For | Learning | Dashboards | Complete Data |

---

## 🎯 When to Use This Method

**Use Get Data - Web when:**
- ✅ You want to **learn** how the YouTube API works
- ✅ You need just the **latest 50 videos**
- ✅ You're **exploring** the data structure
- ✅ You want a **quick test** without coding

**Don't use it when:**
- ❌ You need **all videos** from 2 years (use Method 2)
- ❌ You need **playlist mapping** (use Python - Method 1)
- ❌ You want **automation** (use Method 2)
- ❌ You have **large datasets** (use Method 1 or 2)

---

## 🎓 For Your Manager

**Talking Point:**
> "The Get Data - Web method is great for understanding how the API works, but it's not practical for our full dataset of 2+ years. It would require creating and combining 50+ separate queries manually. That's why I recommend using the Power Query code (Method 2) or Python script (Method 1) for production use."

---

## ✨ Summary

**Method 3: Get Data - Web**
- ✅ Easiest to start
- ✅ No coding needed
- ❌ Not scalable
- ❌ Manual pagination
- 💡 **Best for:** Learning and exploring

**For your use case (2 years of data):**
- Use **Method 2** (Power Query code) ⭐ Recommended
- Or **Method 1** (Python) for complete playlist data

---

## 📝 Quick Start Example

**To get the latest 50 videos (no code):**

1. Get Data > Web
2. URL: `https://www.googleapis.com/youtube/v3/playlistItems?key=AIzaSyBM5DU838aPORBzQE7L3Hv1q7PVGSEQlGU&playlistId=UUUDKhNE_Y_DVkFx1nFNZTWQ&part=snippet,contentDetails&maxResults=50`
3. Transform Data
4. Expand items > Expand contentDetails > videoId
5. Done!

**Result:** 50 video IDs in ~2 minutes

---

**Conclusion:** Great for learning, but use Method 1 or 2 for production! 🚀
