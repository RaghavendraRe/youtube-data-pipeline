import os
import sys
import datetime
import pandas as pd
import requests
import yaml
from dotenv import load_dotenv

# Load .env file
load_dotenv()

from utils.handle_parser import parse_handles_file

# Load Config
try:
    with open("config.yaml", "r") as f:
        config = yaml.safe_load(f)
        API_KEY = os.getenv("YOUTUBE_API_KEY")
        if not API_KEY:
            print("ERROR: YOUTUBE_API_KEY not found in environment.")
            sys.exit(1)
except Exception as e:
    print(f"ERROR loading config: {e}")
    sys.exit(1)

def get_service_url(endpoint):
    return f"https://www.googleapis.com/youtube/v3/{endpoint}?key={API_KEY}"

def get_channel_stats(channel_id):
    """Fetches high-level stats for a single channel."""
    url = get_service_url("channels") + f"&id={channel_id}&part=snippet,statistics,contentDetails"
    response = requests.get(url)
    data = response.json()
    
    if "items" not in data or not data["items"]:
        return None
        
    item = data["items"][0]
    snippet = item["snippet"]
    stats = item["statistics"]
    content = item["contentDetails"]
    
    # Get Last Upload Date
    uploads_id = content["relatedPlaylists"]["uploads"]
    last_upload_date = "N/A"
    
    try:
        # Fetch latest 1 video from uploads
        pl_url = get_service_url("playlistItems") + f"&playlistId={uploads_id}&part=snippet&maxResults=1"
        pl_res = requests.get(pl_url)
        pl_data = pl_res.json()
        if "items" in pl_data and pl_data["items"]:
            pub_str = pl_data["items"][0]["snippet"]["publishedAt"]
            # Clean format
            dt = datetime.datetime.fromisoformat(pub_str.replace("Z", "+00:00"))
            last_upload_date = dt.strftime("%Y-%m-%d")
    except Exception:
        pass

    return {
        "Channel Name": snippet.get("title"),
        "Channel ID": channel_id,
        "Subscriber Count": int(stats.get("subscriberCount", 0)),
        "Total Views": int(stats.get("viewCount", 0)),
        "Total Videos": int(stats.get("videoCount", 0)),
        "Created Date": snippet.get("publishedAt", "")[:10], # Just date YYYY-MM-DD
        "Last Upload Date": last_upload_date,
        "Region (API)": snippet.get("country", "Unknown")
    }

def main():
    print("="*60)
    print(" [INFO] YouTube Channel Audit Tool")
    print("="*60)
    
    INPUT_FILE = "data/handles_list.xlsx"
    OUTPUT_FILE = "data/channel_summary_audit.csv"
    
    channels = parse_handles_file(INPUT_FILE)
    
    if not channels:
        print(" [ERROR] No channels found in Excel. Please check the file.")
        return

    audit_data = []
    
    print(f"Auditing {len(channels)} channels...")
    
    for i, ch in enumerate(channels, 1):
        cid = ch['channel_id']
        wing = ch['wing']
        provided_name = ch['name']
        
        print(f"[{i}/{len(channels)}] Checking: {provided_name} ({cid})...", end=" ")
        
        stats = get_channel_stats(cid)
        
        if stats:
            # Add metadata from Excel
            stats["Wing"] = wing
            stats["Entity Name (Excel)"] = provided_name
            audit_data.append(stats)
            print(" [OK]")
        else:
            print(" [NOT FOUND] (Check ID)")
            # Add a row for failed audits so user knows
            audit_data.append({
                "Channel Name": "NOT FOUND",
                "Channel ID": cid,
                "Wing": wing,
                "Entity Name (Excel)": provided_name,
                "Status": "Invalid ID"
            })
            
    # Save
    if audit_data:
        df = pd.DataFrame(audit_data)
        # Reorder columns for readability
        cols = ["Entity Name (Excel)", "Wing", "Channel Name", "Subscriber Count", "Total Views", "Total Videos", "Last Upload Date", "Created Date", "Region (API)", "Channel ID"]
        # Only use columns that exist
        cols = [c for c in cols if c in df.columns]
        df = df[cols]
        
        df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")
        print("="*60)
        print(f" [DONE] Audit Complete! Saved to: {OUTPUT_FILE}")
        print("="*60)

if __name__ == "__main__":
    main()
