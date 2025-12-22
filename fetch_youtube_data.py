import requests
import csv
import datetime
import re
import os
import json
import sys

# Configuration - Use environment variables for sensitive data
# Configuration - Use environment variables for sensitive data
API_KEY = os.getenv("YOUTUBE_API_KEY") 
CHANNEL_ID = os.getenv("YOUTUBE_CHANNEL_ID", "UCUDKhNE_Y_DVkFx1nFNZTWQ")  # Brahmakumaris

# Output configuration
DATA_DIR = "data"
OUTPUT_FILE = os.path.join(DATA_DIR, "brahmakumaris_videos.csv")

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

def get_service_url(endpoint):
    return f"https://www.googleapis.com/youtube/v3/{endpoint}?key={API_KEY}"

def parse_iso_duration(duration_str):
    """
    Parses ISO 8601 duration string (e.g., PT1H2M10S) to seconds.
    """
    if not duration_str:
        return 0
    
    match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', duration_str)
    if not match:
        return 0
    
    hours = int(match.group(1) or 0)
    minutes = int(match.group(2) or 0)
    seconds = int(match.group(3) or 0)
    
    return hours * 3600 + minutes * 60 + seconds

def get_uploads_playlist_id(channel_id):
    url = get_service_url("channels") + f"&id={channel_id}&part=contentDetails"
    response = requests.get(url)
    data = response.json()
    
    if "items" not in data or not data["items"]:
        raise Exception(f"Channel not found or API error: {data}")
        
    return data["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]

def get_all_playlists(channel_id):
    """
    Fetches all playlists (Podcasts) for the channel.
    Returns a dict: {playlist_id: playlist_title}
    """
    playlists = {}
    next_page_token = None
    print("Fetching all playlists/podcasts...")
    
    while True:
        url = get_service_url("playlists") + f"&channelId={channel_id}&part=snippet&maxResults=50"
        if next_page_token:
            url += f"&pageToken={next_page_token}"
            
        response = requests.get(url)
        data = response.json()
        
        if "items" not in data:
            break
            
        for item in data["items"]:
            pid = item["id"]
            title = item["snippet"]["title"]
            playlists[pid] = title
            
        next_page_token = data.get("nextPageToken")
        if not next_page_token:
            break
            
    print(f"Found {len(playlists)} playlists.")
    return playlists

def map_videos_to_playlists(playlists):
    """
    Iterates through all playlists and maps video IDs to their Playlist Names.
    Returns: {video_id: [list_of_playlist_names]}
    """
    video_map = {}
    print("Mapping videos to playlists (this may take a moment)...")
    
    for pid, ptitle in playlists.items():
        next_page_token = None
        while True:
            # We only need contentDetails to save quota/bandwidth, but snippet is safer for debugging
            url = get_service_url("playlistItems") + f"&playlistId={pid}&part=contentDetails&maxResults=50"
            if next_page_token:
                url += f"&pageToken={next_page_token}"
                
            response = requests.get(url)
            data = response.json()
            
            if "items" not in data:
                break
                
            for item in data["items"]:
                vid = item["contentDetails"]["videoId"]
                if vid not in video_map:
                    video_map[vid] = []
                # Avoid duplicates
                if ptitle not in video_map[vid]:
                    video_map[vid].append(ptitle)
            
            next_page_token = data.get("nextPageToken")
            if not next_page_token:
                break
                
    return video_map

def fetch_videos(uploads_playlist_id, podcast_map):
    videos = []
    next_page_token = None
    two_years_ago = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=730)
    
    print(f"Fetching videos from the last 2 years (since {two_years_ago.date()})...")
    
    while True:
        url = get_service_url("playlistItems") + f"&playlistId={uploads_playlist_id}&part=snippet,contentDetails&maxResults=50"
        if next_page_token:
            url += f"&pageToken={next_page_token}"
            
        response = requests.get(url)
        data = response.json()
        
        if "items" not in data:
            print(f"Error fetching playlist items: {data}")
            break
            
        video_ids = []
        for item in data["items"]:
            published_at_str = item["snippet"]["publishedAt"]
            published_at = datetime.datetime.fromisoformat(published_at_str.replace("Z", "+00:00"))
            
            if published_at < two_years_ago:
                print("Reached videos older than 2 years. Stopping fetch.")
                return videos
            
            video_ids.append(item["contentDetails"]["videoId"])
            
        if not video_ids:
            break
            
        # Fetch detailed stats for these videos
        videos_details = get_video_details(video_ids, podcast_map)
        videos.extend(videos_details)
        
        print(f"Fetched {len(videos)} videos so far...")
        
        next_page_token = data.get("nextPageToken")
        if not next_page_token:
            break
            
    return videos

OFFICIAL_PODCAST_TITLES = [
    "Mindful Moments | Brahma Kumaris Podcast",
    "Climate Wisdom - COP30 Belem, Brasil",
    "The Spiritual Empress - Dadi Prakashmani",
    "COP 29 Baku - Climate Wisdom | Brahma Kumaris",
    "Care, Share, Inspire - Climate Wisdom from COP28 Dubai",
    "Companion of God - Dadi Janki (with English Translation)"
]

def get_video_details(video_ids, podcast_map):
    url = get_service_url("videos") + f"&id={','.join(video_ids)}&part=snippet,contentDetails,statistics,liveStreamingDetails"
    response = requests.get(url)
    data = response.json()
    
    details_list = []
    if "items" not in data:
        return []

    for item in data["items"]:
        vid = item["id"]
        snippet = item["snippet"]
        statistics = item["statistics"]
        content_details = item["contentDetails"]
        live_streaming = item.get("liveStreamingDetails", {})
        
        # Safe extraction
        view_count = int(statistics.get("viewCount", 0))
        like_count = int(statistics.get("likeCount", 0))
        comment_count = int(statistics.get("commentCount", 0))
        duration_iso = content_details.get("duration", "PT0S")
        duration_seconds = parse_iso_duration(duration_iso)
        
        # Metrics
        engagement = like_count + comment_count
        engagement_rate = (engagement / view_count) if view_count > 0 else 0

        # Tags
        tags = "|".join(snippet.get("tags", []))
        
        # Type Logic
        video_type = "Long"
        is_short = False
        is_live = False
        
        if live_streaming: 
             is_live = True
             video_type = "Live"
        elif duration_seconds <= 60 and duration_seconds > 0:
             is_short = True
             video_type = "Short"

        published_at = snippet.get("publishedAt")

        # Date Formatting (Remove T and Z)
        if published_at:
             dt = datetime.datetime.fromisoformat(published_at.replace("Z", "+00:00"))
             published_at = dt.strftime("%Y-%m-%d %H:%M:%S")

        # Podcast Logic
        all_playlist_names = podcast_map.get(vid, [])
        all_playlists_str = "|".join(all_playlist_names) if all_playlist_names else ""
        
        # Filter for Official Podcasts
        # We use a loose match to ensure we catch them (e.g., if title changes slightly)
        found_officials = []
        for pl_name in all_playlist_names:
            # Check if this playlist name matches any of our known official titles
            # We normalize simpler checks
            for official_title in OFFICIAL_PODCAST_TITLES:
                # Check for exact or very close substring match
                if official_title in pl_name or pl_name in official_title:
                   if pl_name not in found_officials:
                       found_officials.append(pl_name)

        official_podcast_str = "|".join(found_officials) if found_officials else None

        # Create Record with User-Requested Column Names
        record = {
            "Video ID": vid,
            "Video URL": f"https://www.youtube.com/watch?v={vid}",
            "Title": snippet.get("title", ""),
            "Description": snippet.get("description", ""),
            "Published Date": published_at,
            "Duration (Sec)": duration_seconds,
            "Duration (ISO)": duration_iso,
            "Is Short": is_short,
            "Is Live": is_live,
            "Video Type": video_type,
            "Views": view_count,
            "Likes": like_count,
            "Comments": comment_count,
            "Engagement": engagement,
            "Engagement Rate": round(engagement_rate, 4),
            "Tags": tags,
            "All Playlists": all_playlists_str,       # Renamed from podcast_name
            "Podcast Name": official_podcast_str,     # NEW: Only official podcasts
            "Category ID": snippet.get("categoryId", ""),
            "Channel Title": snippet.get("channelTitle", ""),
            "Definition (HD/SD)": content_details.get("definition", ""),
            "Live Start": live_streaming.get("actualStartTime", ""),
            "Live End": live_streaming.get("actualEndTime", ""),
            "Last Updated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        details_list.append(record)
        
    return details_list

def save_to_csv(videos, filename):
    if not videos:
        print("No videos to save.")
        return

    keys = videos[0].keys()
    
    # Use utf-8-sig to ensure Excel opens special characters correctly
    with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
        dict_writer = csv.DictWriter(f, fieldnames=keys)
        dict_writer.writeheader()
        dict_writer.writerows(videos)
    
    print(f"Saved {len(videos)} videos to {filename}")

def main():
    try:
        print("="*60)
        print("YouTube Data Collection - Brahmakumaris")
        print(f"Started at: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)
        
        # Validate API key
        if not API_KEY or API_KEY == "":
            print("❌ ERROR: YOUTUBE_API_KEY environment variable not set!")
            sys.exit(1)
        
        print(f"✓ API Key: {'*' * 20}{API_KEY[-4:]}")
        print(f"✓ Channel ID: {CHANNEL_ID}")
        print(f"✓ Output File: {OUTPUT_FILE}")
        print()
        
        uploads_id = get_uploads_playlist_id(CHANNEL_ID)
        print(f"✓ Uploads Playlist ID: {uploads_id}\n")
        
        # 1. Fetch Playlists (Podcasts)
        playlists = get_all_playlists(CHANNEL_ID)
        
        # 2. Map Videos to Playlists
        podcast_map = map_videos_to_playlists(playlists)
        
        # 3. Fetch Main Videos with mapping
        videos = fetch_videos(uploads_id, podcast_map)
        
        save_to_csv(videos, OUTPUT_FILE)
        
        print()
        print("="*60)
        print(f"✅ SUCCESS: Collected {len(videos)} videos")
        print(f"✅ Saved to: {OUTPUT_FILE}")
        print(f"Completed at: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)
        
    except Exception as e:
        print()
        print("="*60)
        print(f"❌ ERROR: {e}")
        print("="*60)
        sys.exit(1)

if __name__ == "__main__":
    main()
