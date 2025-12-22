
import csv
import sys

def load_csv(filename):
    with open(filename, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        data = list(reader)
        fieldnames = reader.fieldnames
    return fieldnames, data

def compare_csvs(file_v2, file_v3):
    print(f"Loading {file_v2}...")
    headers_v2, data_v2 = load_csv(file_v2)
    print(f"Loading {file_v3}...")
    headers_v3, data_v3 = load_csv(file_v3)

    # 1. Compare Columns
    print(f"\n--- Column Comparison ---")
    set_v2 = set(headers_v2)
    set_v3 = set(headers_v3)
    
    new_cols = set_v3 - set_v2
    missing_cols = set_v2 - set_v3
    
    print(f"Columns in v2: {len(headers_v2)}")
    print(f"Columns in v3: {len(headers_v3)}")
    
    if new_cols:
        print(f"New columns in v3: {new_cols}")
    if missing_cols:
        print(f"Missing columns in v3: {missing_cols}") # Should be empty
        
    # 2. Compare Row Counts
    print(f"\n--- Row Count Comparison ---")
    print(f"Rows in v2: {len(data_v2)}")
    print(f"Rows in v3: {len(data_v3)}")
    
    if len(data_v2) == len(data_v3):
        print("Row counts match.")
    else:
        print(f"Row count mismatch! Difference: {len(data_v3) - len(data_v2)}")

    # 3. Compare Data Content (common columns)
    print(f"\n--- Content Comparison (First 5 records for common columns) ---")
    common_cols = list(set_v2.intersection(set_v3))
    
    # Map by videoId for accurate comparison
    dict_v2 = {row['videoId']: row for row in data_v2}
    dict_v3 = {row['videoId']: row for row in data_v3}
    
    # Check for IDs present in one but not other
    ids_v2 = set(dict_v2.keys())
    ids_v3 = set(dict_v3.keys())
    
    only_in_v2 = ids_v2 - ids_v3
    only_in_v3 = ids_v3 - ids_v2
    
    if only_in_v2:
        print(f"Video IDs only in v2: {len(only_in_v2)}")
    if only_in_v3:
        print(f"Video IDs only in v3: {len(only_in_v3)}")

    # Check differences in values for common IDs
    print("\nChecking value differences for common Video IDs...")
    diff_count = 0
    checked_count = 0
    
    diff_examples = {} # col -> (val_v2, val_v3)

    for vid_id in ids_v2.intersection(ids_v3):
        row_v2 = dict_v2[vid_id]
        row_v3 = dict_v3[vid_id]
        checked_count += 1
        
        for col in common_cols:
            val_v2 = row_v2.get(col, "")
            val_v3 = row_v3.get(col, "")
            
            if val_v2 != val_v3:
                # Ignore negligible differences if necessary, but report first
                if col not in diff_examples:
                    diff_examples[col] = (val_v2, val_v3)
                diff_count += 1

    if diff_examples:
        print("Found differences in the following columns (showing first mismatch found):")
        for col, (v2, v3) in diff_examples.items():
            print(f"  Column '{col}': v2='{v2}'  vs  v3='{v3}'")
    else:
        print("No differences found in common columns.")

if __name__ == "__main__":
    compare_csvs("brahmakumaris_videos_v2.csv", "brahmakumaris_videos_v3.csv")
