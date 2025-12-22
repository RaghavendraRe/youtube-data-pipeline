# Project Documentation: YouTube Data Collection

## 1. Approach: How we fetched the data
We used the **YouTube Data API v3** (Google's official API), which is the standard and most reliable method for collecting channel data.

**Why API and not Web Scraping?**
-   **Reliability**: The API provides structured data directly from YouTube's database. Web scraping (like BeautifulSoup or Selenium) breaks easily when YouTube changes its website design.
-   **Efficiency**: The API can fetch details for 50 videos in one split-second request. Scraping would require loading 1600+ individual pages.
-   **Accuracy**: We get exact numbers (e.g., `viewCount` = 12,504) rather than rounded text often shown on the UI (e.g., "12K views").

**The Process (implemented in `fetch_youtube_data.py`):**
1.  **Get Channel ID**: Identified Brahmakumaris channel ID (`UCUDKhNE_Y_DVkFx1nFNZTWQ`).
2.  **Get "Uploads" Playlist**: Every channel has a hidden "playlist" that contains all their uploads. We fetched this ID.
3.  **Paginate**: We looped through this playlist to get the list of all video IDs for the last 2 years.
4.  **Batch Details**: We sent these Video IDs in batches of 50 to the API to get rich metadata (duration, likes, comments, tags).
5.  **Calculate & Save**: We processed the raw data (e.g., converting "PT5M" duration to seconds) and saved it to `brahmakumaris_videos.csv`.

---

## 2. Data Dictionary (Column Definitions)
Here is the explanation of every column in your CSV file:

| Column Name | Description |
| :--- | :--- |
| `videoId` | Unique ID for the video (e.g., `ooB-f2HMWKQ`). |
| `videoUrl` | Clickable link to watch the video. |
| `title` | The full title of the video. |
| `description` | The text description under the video. |
| `publishedAt` | The exact date and time the video was uploaded (formatted as `YYYY-MM-DD HH:MM:SS`). |
| `duration_seconds` | Length of the video in seconds (useful for filtering Short vs Long). |
| `duration_iso` | Raw duration format from YouTube (e.g., `PT5M20S` means 5 mins 20 secs). |
| `is_short` | `True` if video is likely a Short (< 60s), `False` otherwise. |
| `is_live` | `True` if the video was a Livestream. |
| **`video_type`** | **Categories: "Short", "Long", or "Live". (This is the column you asked for).** |
| `viewCount` | Total number of views. |
| `likeCount` | Total number of likes. |
| `commentCount` | Total number of comments. |
| `engagement` | Sum of interactions (`likeCount` + `commentCount`). |
| `engagement_rate` | Ratio of Engagement to Views (`engagement / viewCount`). Good for measuring content quality relative to reach. |
| `tags` | Keywords associated with the video, separated by `|`. |
| `categoryId` | YouTube's internal category ID (e.g., "27" often means Education or Non-profit). |
| `channelTitle` | Channel Name (Brahmakumaris). |
| `definition` | Video quality (usually "hd" or "sd"). |
| `live_actual_start` | If it was a live stream, when it actually started. |
| `live_actual_end` | If it was a live stream, when it ended. |
| `raw_json_path` | Unused placeholder (set to "N/A"). |
| `first_fetched_at` | Timestamp of when this record was first downloaded. |
| `last_fetched_at` | Timestamp of when this record was last updated. |

---

## 3. Analysis Suggestions
### Are there missing columns?
For a standard analysis, you have everything you need. However, for deeper Power BI analysis, you might want to **calculate** these simple new columns inside Power BI (using DAX or Power Query) based on the `publishedAt` date:
1.  **`Day of Week`**: Does the channel get more views on specific days (e.g., Sunday vs Monday)?
2.  **`Hour of Day`**: What is the best time to upload?
3.  **`Title Length`**: Do shorter or longer titles perform better? (Length of `title` column).
4.  **`Tag Count`**: Does using more tags correlate with more views? (Count of items in `tags`).

You do **not** need to re-fetch data for these; you can derive them from your existing file.
