# Data Directory

This directory stores the YouTube data collected by the automated pipeline.

## Files

- `brahmakumaris_videos.csv` - Main output file containing video data
  - Updated automatically by GitHub Actions
  - Contains 2 years of video history
  - Includes views, likes, comments, engagement metrics, and podcast information

## Data Schema

| Column | Type | Description |
|--------|------|-------------|
| Video ID | String | Unique YouTube video identifier |
| Video URL | String | Full YouTube watch URL |
| Title | String | Video title |
| Description | Text | Video description |
| Published Date | DateTime | When video was published |
| Duration (Sec) | Integer | Video length in seconds |
| Duration (ISO) | String | ISO 8601 duration format |
| Is Short | Boolean | True if YouTube Short |
| Is Live | Boolean | True if live stream |
| Video Type | String | Short/Live/Long |
| Views | Integer | Total view count |
| Likes | Integer | Total likes |
| Comments | Integer | Total comments |
| Engagement | Integer | Likes + Comments |
| Engagement Rate | Float | Engagement / Views |
| Tags | String | Pipe-separated tags |
| All Playlists | String | All playlists containing this video |
| Podcast Name | String | Official podcast name (if applicable) |
| Category ID | String | YouTube category |
| Channel Title | String | Channel name |
| Definition (HD/SD) | String | Video quality |
| Live Start | DateTime | Live stream start time |
| Live End | DateTime | Live stream end time |
| Last Updated | DateTime | When data was last fetched |

## Notes

- File is automatically updated daily via GitHub Actions
- Power BI connects to this file for dashboard
- Historical data is preserved and updated incrementally
