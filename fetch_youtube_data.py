import requests
import csv
import datetime
import re
import os
import json
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

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

def fetch_videos(uploads_playlist_id):
    videos = []
    next_page_token = None
    import yaml
    import yaml
    try:
        with open("config.yaml", "r") as f:
            config = yaml.safe_load(f)
            days_history = config["youtube"].get("days_history", 730)
    except:
        days_history = 36500 # Default to full history if config fails
        
    two_years_ago = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=days_history)
    
    print(f"Fetching videos from the last {days_history} days (since {two_years_ago.date()})...")
    
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
        videos_details = get_video_details(video_ids)
        videos.extend(videos_details)
        
        print(f"Fetched {len(videos)} videos so far...")
        
        next_page_token = data.get("nextPageToken")
        if not next_page_token:
            break
            
    return videos

def get_video_details(video_ids):
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

        # Create Record with User-Requested Column Names
        # Description, Tags, Playlists, Podcast Name, Category ID REMOVED as per request
        record = {
            "Video ID": vid,
            "Video URL": f"https://www.youtube.com/watch?v={vid}",
            "Title": snippet.get("title", ""),
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
            "Channel ID": snippet.get("channelId", ""),
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
            print(" [ERROR] YOUTUBE_API_KEY environment variable not set!")
            sys.exit(1)
        
        print(f" [INFO] API Key: {'*' * 20}{API_KEY[-4:]}")
        print(f" [INFO] Output File: {OUTPUT_FILE}")
        print()
        
        # 1. Load Channels from Excel
        print("Loading channels from Excel...")
        from utils.handle_parser import parse_handles_file
        from utils.handle_parser import parse_handles_file
        INPUT_FILE = "data/handles_list.xlsx"
        
        channels = parse_handles_file(INPUT_FILE)
        
        if not channels:
            print(" [ERROR] No channels found. Exiting.")
            sys.exit(1)
            
        all_videos = []
        total_channels = len(channels)
        
        print(f" [START] Starting collection for {total_channels} channels...")
        
        # 2. Iterate through each channel
        for i, channel in enumerate(channels, 1):
            try:
                cid = channel['channel_id']
                cname = channel['name']
                wing = channel['wing']
                
                print(f"\n[{i}/{total_channels}] Processing: {cname} ({cid}) - [{wing}]")
                
                # Fetch Uploads Playlist ID
                try:
                    uploads_id = get_uploads_playlist_id(cid)
                except Exception as e:
                    print(f"  [SKIP] Skipping {cname}: {e}")
                    continue

                # Fetch Main Videos (No podcast mapping needed anymore)
                videos = fetch_videos(uploads_id)
                
                # Enrich Data with Wing and Entity Name
                for v in videos:
                    v['Wing'] = wing
                    v['Entity Name'] = cname
                    
                all_videos.extend(videos)
                print(f"  [OK] Added {len(videos)} videos from {cname}")
                
            except Exception as e:
                print(f"  [ERROR] Error processing channel {cname}: {e}")

        # 3. Save Combined Data
        save_to_csv(all_videos, OUTPUT_FILE)
        
        print()
        print("="*60)
        print(f" [DONE] SUCCESS: Collected {len(all_videos)} videos")
        print(f" [DONE] Saved to: {OUTPUT_FILE}")
        print(f"Completed at: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)
        
    except Exception as e:
        print()
        print("="*60)
        print(f" [ERROR] {e}")
        print("="*60)
        sys.exit(1)

if __name__ == "__main__":
    main()
