import pandas as pd
import os

def parse_handles_file(file_path):
    """
    Parses the BK Social Media Handles Excel file.
    Expected columns: 'Channel ID', 'Wing' (from section headers), 'Entity Name' (Index 1).
    
    Returns:
        list of dicts: [{'channel_id': '...', 'name': '...', 'wing': '...'}]
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Input file not found: {file_path}")

    print(f"Reading input file: {file_path}")
    
    # Read the standardized Excel file
    try:
        df = pd.read_excel(file_path)
    except Exception as e:
        print(f"❌ Error reading Excel file: {e}")
        return []

    # Expected columns: Wing, Entity Name, URL, Channel ID
    # Normalize columns to lowercase for safe checking
    df.columns = df.columns.astype(str).str.strip()
    
    # Check for required 'Channel ID' column
    # We look for exact match or close match
    id_col = next((c for c in df.columns if "Channel ID" in c or "channel id" in c.lower()), None)
    
    if not id_col:
        print(" [WARN] 'Channel ID' column not found. Available columns:", df.columns.tolist())
        return []
        
    channels = []
    for index, row in df.iterrows():
        channel_id = str(row[id_col]).strip()
        
        # Validate ID
        if channel_id and channel_id.startswith("UC"):
            channels.append({
                "channel_id": channel_id,
                "name": str(row.get("Entity Name", "Unknown")).strip(),
                "wing": str(row.get("Wing", "General")).strip()
            })
            
    print(f" [OK] Found {len(channels)} valid channels.")
    return channels

if __name__ == "__main__":
    # Test run
    res = parse_handles_file("../data/handles_list.xlsx")
    print(res[:3])
