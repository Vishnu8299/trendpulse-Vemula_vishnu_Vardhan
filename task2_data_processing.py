"""
TrendPulse - Task 2: Clean Data & Save as CSV
==============================================
Author : Vishnu Vardhan Vemula
Date   : 2026-04-08

What this script does:
  1. Loads the JSON data from Task 1 into a Pandas DataFrame
  2. Cleans the data by removing duplicates, fixing missing values, and filtering
  3. Saves the cleaned data as a CSV file for further analysis
  4. Provides detailed progress reporting at each cleaning step

Input:  data/trends_YYYYMMDD.json (from Task 1)
Output: data/trends_clean.csv
"""

import pandas as pd
import json
import os
import glob
from datetime import datetime

def find_latest_json_file():
    """
    Find the most recent JSON file in the data/ folder.
    Returns the filename or None if no JSON files found.
    """
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
    """
    Load JSON data from file into a Pandas DataFrame.
    Returns DataFrame and number of rows loaded.
    """
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
    """
    Remove duplicate rows based on post_id.
    Returns cleaned DataFrame and number of duplicates removed.
    """
    original_count = len(df)
    
    # Remove duplicates based on post_id, keep first occurrence
    df_cleaned = df.drop_duplicates(subset=['post_id'], keep='first')
    duplicates_removed = original_count - len(df_cleaned)
    
    print(f"After removing duplicates: {len(df_cleaned)}")
    return df_cleaned, duplicates_removed

def handle_missing_values(df):
    """
    Remove rows with missing critical values (post_id, title, score).
    Returns cleaned DataFrame and number of rows removed.
    """
    original_count = len(df)
    
    # Check for missing values in critical columns
    missing_critical = df[['post_id', 'title', 'score']].isnull().any(axis=1)
    df_cleaned = df[~missing_critical]
    
    rows_removed = original_count - len(df_cleaned)
    print(f"After removing nulls: {len(df_cleaned)}")
    return df_cleaned, rows_removed

def fix_data_types(df):
    """
    Convert score and num_comments to integers.
    Returns DataFrame with corrected data types.
    """
    # Convert score to integer, handling any non-numeric values
    df['score'] = pd.to_numeric(df['score'], errors='coerce').fillna(0).astype(int)
    
    # Convert num_comments to integer, handling any non-numeric values
    df['num_comments'] = pd.to_numeric(df['num_comments'], errors='coerce').fillna(0).astype(int)
    
    return df

def filter_low_quality_stories(df, min_score=5):
    """
    Remove stories with score less than the minimum threshold.
    Returns filtered DataFrame and number of rows removed.
    """
    original_count = len(df)
    
    # Filter stories with score >= min_score
    df_filtered = df[df['score'] >= min_score]
    
    rows_removed = original_count - len(df_filtered)
    print(f"After removing low scores: {len(df_filtered)}")
    return df_filtered, rows_removed

def clean_text_data(df):
    """
    Clean text columns by stripping whitespace.
    Returns DataFrame with cleaned text data.
    """
    # Strip whitespace from title column
    df['title'] = df['title'].str.strip()
    
    # Also clean other text columns if they exist
    if 'author' in df.columns:
        df['author'] = df['author'].str.strip()
    
    if 'category' in df.columns:
        df['category'] = df['category'].str.strip()
    
    return df

def save_to_csv(df, filepath):
    """
    Save DataFrame to CSV file.
    Returns True if successful, False otherwise.
    """
    try:
        df.to_csv(filepath, index=False, encoding='utf-8')
        print(f"Saved {len(df)} rows to {filepath}")
        return True
    except Exception as e:
        print(f"Error saving CSV: {e}")
        return False

def print_category_summary(df):
    """
    Print summary of stories per category.
    """
    print("\nStories per category:")
    
    if 'category' in df.columns:
        category_counts = df['category'].value_counts()
        for category, count in category_counts.items():
            print(f"  {category:<15} {count}")
    else:
        print("  No category column found in data")

def main():
    """
    Main function to orchestrate the data cleaning process.
    """
    print("=" * 50)
    print("  TrendPulse – Task 2: Data Cleaning & CSV Export")
    print("=" * 50)
    print()
    
    # Step 1: Find and load the latest JSON file
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
    
    # Step 2: Clean the data
    print("[Step 2] Cleaning data...")
    
    # Remove duplicates
    df, dup_count = remove_duplicates(df)
    
    # Handle missing values
    df, null_count = handle_missing_values(df)
    
    # Fix data types
    df = fix_data_types(df)
    
    # Filter low-quality stories
    df, low_score_count = filter_low_quality_stories(df, min_score=5)
    
    # Clean text data
    df = clean_text_data(df)
    
    print()
    
    # Step 3: Save to CSV
    print("[Step 3] Saving to CSV...")
    
    # Create data directory if it doesn't exist
    os.makedirs("data", exist_ok=True)
    
    # Save cleaned data
    csv_file = "data/trends_clean.csv"
    success = save_to_csv(df, csv_file)
    
    if not success:
        print("Failed to save CSV file. Exiting.")
        return
    
    print()
    
    # Step 4: Print summary
    print_category_summary(df)
    
    print()
    print("Data cleaning completed successfully! ✓")
    
    # Optional: Print cleaning summary
    total_removed = dup_count + null_count + low_score_count
    print(f"\nCleaning summary:")
    print(f"  Duplicates removed: {dup_count}")
    print(f"  Null values removed: {null_count}")
    print(f"  Low score stories removed: {low_score_count}")
    print(f"  Total rows removed: {total_removed}")
    print(f"  Final dataset: {len(df)} rows")

if __name__ == "__main__":
    main()
