import pandas as pd
import json
import os
import glob
from datetime import datetime

def find_latest_json_file():
    data_dir = "data"
    if not os.path.exists(data_dir):
        print(f"Error: {data_dir} directory not found!")
        return None
    
    # Look for trends_*.json files and sort by date
    pattern = os.path.join(data_dir, "trends_*.json")
    json_files = glob.glob(pattern)
    
    if not json_files:
        print("Error: No trends_*.json files found in data/ directory!")
        return None
    
    # Sort by filename (which includes date) to get the latest
    latest_file = max(json_files)
    return latest_file

def load_json_data(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        df = pd.DataFrame(data)
        print(f"Loaded {len(df)} stories from {filepath}")
        return df
    
    except FileNotFoundError:
        print(f"Error: File {filepath} not found!")
        return None
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {filepath}: {e}")
        return None
    except Exception as e:
        print(f"Error loading data: {e}")
        return None

def remove_duplicates(df):
    original_count = len(df)
    
    # Remove duplicates based on post_id, keep first occurrence
    df_cleaned = df.drop_duplicates(subset=['post_id'], keep='first')
    duplicates_removed = original_count - len(df_cleaned)
    
    print(f"After removing duplicates: {len(df_cleaned)}")
    return df_cleaned, duplicates_removed

def handle_missing_values(df):
    original_count = len(df)
    
    # Check for missing values in critical columns
    missing_critical = df[['post_id', 'title', 'score']].isnull().any(axis=1)
    df_cleaned = df[~missing_critical]
    
    rows_removed = original_count - len(df_cleaned)
    print(f"After removing nulls: {len(df_cleaned)}")
    return df_cleaned, rows_removed

def fix_data_types(df):
    # Convert score to integer, handling any non-numeric values
    df['score'] = pd.to_numeric(df['score'], errors='coerce').fillna(0).astype(int)
    
    # Convert num_comments to integer, handling any non-numeric values
    df['num_comments'] = pd.to_numeric(df['num_comments'], errors='coerce').fillna(0).astype(int)
    
    return df

def filter_low_quality_stories(df, min_score=5):
    original_count = len(df)
    
    # Filter stories with score >= min_score
    df_filtered = df[df['score'] >= min_score]
    
    rows_removed = original_count - len(df_filtered)
    print(f"After removing low scores: {len(df_filtered)}")
    return df_filtered, rows_removed

def clean_text_data(df):
    # Strip whitespace from title column
    df['title'] = df['title'].str.strip()
    
    # Also clean other text columns if they exist
    if 'author' in df.columns:
        df['author'] = df['author'].str.strip()
    
    if 'category' in df.columns:
        df['category'] = df['category'].str.strip()
    
    return df

def save_to_csv(df, filepath):
    try:
        df.to_csv(filepath, index=False, encoding='utf-8')
        print(f"Saved {len(df)} rows to {filepath}")
        return True
    except Exception as e:
        print(f"Error saving CSV: {e}")
        return False

def print_category_summary(df):
    print("\nStories per category:")
    
    if 'category' in df.columns:
        category_counts = df['category'].value_counts()
        for category, count in category_counts.items():
            print(f"  {category:<15} {count}")
    else:
        print("  No category column found in data")

def main():
    print("=" * 50)
    print("  TrendPulse – Task 2: Data Cleaning & CSV Export")
    print("=" * 50)
    print()
    
    print("[Step 1] Loading JSON data...")
    json_file = find_latest_json_file()
    
    if json_file is None:
        print("Cannot proceed without JSON data. Exiting.")
        return
    
    df = load_json_data(json_file)
    if df is None:
        print("Failed to load data. Exiting.")
        return
    
    print()
    
    print("[Step 2] Cleaning data...")
    
    df, dup_count = remove_duplicates(df)
    df, null_count = handle_missing_values(df)
    df = fix_data_types(df)
    df, low_score_count = filter_low_quality_stories(df, min_score=5)
    df = clean_text_data(df)
    
    print()
    
    print("[Step 3] Saving to CSV...")
    
    os.makedirs("data", exist_ok=True)
    
    csv_file = "data/trends_clean.csv"
    success = save_to_csv(df, csv_file)
    
    if not success:
        print("Failed to save CSV file. Exiting.")
        return
    
    print()
    print_category_summary(df)
    
    print()
    print("Data cleaning completed successfully! ✓")
    total_removed = dup_count + null_count + low_score_count
    print(f"\nCleaning summary:")
    print(f"  Duplicates removed: {dup_count}")
    print(f"  Null values removed: {null_count}")
    print(f"  Low score stories removed: {low_score_count}")
    print(f"  Total rows removed: {total_removed}")
    print(f"  Final dataset: {len(df)} rows")

if __name__ == "__main__":
    main()
