"""
TrendPulse - Task 3: Analysis with Pandas & NumPy
==================================================
Author : Vishnu Vardhan Vemula
Date   : 2026-04-08

What this script does:
  1. Loads the cleaned CSV data from Task 2
  2. Performs statistical analysis using NumPy and Pandas
  3. Finds patterns and insights in the trending stories data
  4. Adds new calculated columns (engagement and is_popular)
  5. Saves the enhanced dataset for visualization in Task 4

Input:  data/trends_clean.csv (from Task 2)
Output: data/trends_analysed.csv
"""

import pandas as pd
import numpy as np
import os

def load_clean_data(filepath):
    """
    Load the cleaned CSV data into a Pandas DataFrame.
    Returns DataFrame and basic info about the loaded data.
    """
    try:
        df = pd.read_csv(filepath)
        print(f"Loaded data: {df.shape}")
        return df
    except FileNotFoundError:
        print(f"Error: File {filepath} not found!")
        return None
    except Exception as e:
        print(f"Error loading data: {e}")
        return None

def display_basic_info(df):
    """
    Display basic information about the dataset.
    """
    print("\nFirst 5 rows:")
    print(df.head())
    
    print(f"\nDataset shape: {df.shape} (rows, columns)")
    
    # Calculate and print averages
    avg_score = df['score'].mean()
    avg_comments = df['num_comments'].mean()
    
    print(f"\nAverage score   : {avg_score:,.0f}")
    print(f"Average comments: {avg_comments:,.0f}")
    
    return avg_score

def calculate_numpy_statistics(df):
    """
    Use NumPy to calculate statistical measures for the score column.
    """
    print("\n--- NumPy Stats ---")
    
    # Convert score to NumPy array for calculations
    scores = df['score'].values
    
    # Calculate statistics using NumPy
    mean_score = np.mean(scores)
    median_score = np.median(scores)
    std_score = np.std(scores)
    max_score = np.max(scores)
    min_score = np.min(scores)
    
    print(f"Mean score   : {mean_score:,.0f}")
    print(f"Median score : {median_score:,.0f}")
    print(f"Std deviation: {std_score:,.0f}")
    print(f"Max score    : {max_score:,.0f}")
    print(f"Min score    : {min_score:,.0f}")
    
    return mean_score

def analyze_categories(df):
    """
    Find which category has the most stories.
    """
    category_counts = df['category'].value_counts()
    most_common_category = category_counts.index[0]
    most_common_count = category_counts.iloc[0]
    
    print(f"\nMost stories in: {most_common_category} ({most_common_count} stories)")
    
    return category_counts

def find_most_commented_story(df):
    """
    Find the story with the most comments.
    """
    # Get the row with maximum comments
    most_commented_idx = df['num_comments'].idxmax()
    most_commented_story = df.loc[most_commented_idx]
    
    title = most_commented_story['title']
    comment_count = most_commented_story['num_comments']
    
    print(f"\nMost commented story: \"{title}\" — {comment_count:,} comments")
    
    return most_commented_story

def add_engagement_column(df):
    """
    Add engagement column: num_comments / (score + 1)
    This measures discussion per upvote.
    """
    # Calculate engagement ratio
    df['engagement'] = df['num_comments'] / (df['score'] + 1)
    
    print(f"\nAdded 'engagement' column (comments per upvote)")
    print(f"Engagement range: {df['engagement'].min():.3f} to {df['engagement'].max():.3f}")
    
    return df

def add_popularity_column(df, avg_score):
    """
    Add is_popular column: True if score > average score, else False
    """
    df['is_popular'] = df['score'] > avg_score
    
    popular_count = df['is_popular'].sum()
    total_count = len(df)
    
    print(f"Added 'is_popular' column")
    print(f"Popular stories: {popular_count}/{total_count} ({popular_count/total_count*100:.1f}%)")
    
    return df

def save_analysed_data(df, filepath):
    """
    Save the analysed DataFrame to CSV.
    """
    try:
        df.to_csv(filepath, index=False)
        print(f"\nSaved to {filepath}")
        return True
    except Exception as e:
        print(f"Error saving file: {e}")
        return False

def print_summary_statistics(df):
    """
    Print additional summary statistics for insights.
    """
    print(f"\n--- Additional Insights ---")
    
    # Engagement by category
    engagement_by_category = df.groupby('category')['engagement'].mean().sort_values(ascending=False)
    print(f"\nAverage engagement by category:")
    for category, engagement in engagement_by_category.items():
        print(f"  {category:<15}: {engagement:.3f}")
    
    # Popular stories by category
    popular_by_category = df[df['is_popular']].groupby('category').size().sort_values(ascending=False)
    print(f"\nPopular stories by category:")
    for category, count in popular_by_category.items():
        total_in_category = df[df['category'] == category].shape[0]
        percentage = (count / total_in_category) * 100
        print(f"  {category:<15}: {count}/{total_in_category} ({percentage:.1f}%)")

def main():
    """
    Main function to orchestrate the data analysis process.
    """
    print("=" * 60)
    print("  TrendPulse – Task 3: Data Analysis with Pandas & NumPy")
    print("=" * 60)
    
    # Step 1: Load and explore the data
    print("\n[Step 1] Loading and exploring data...")
    
    csv_file = "data/trends_clean.csv"
    df = load_clean_data(csv_file)
    
    if df is None:
        print("Failed to load data. Exiting.")
        return
    
    # Display basic information
    avg_score = display_basic_info(df)
    
    # Step 2: NumPy statistical analysis
    print("\n[Step 2] NumPy statistical analysis...")
    
    mean_score = calculate_numpy_statistics(df)
    category_counts = analyze_categories(df)
    most_commented = find_most_commented_story(df)
    
    # Step 3: Add new columns
    print("\n[Step 3] Adding new columns...")
    
    # Add engagement column
    df = add_engagement_column(df)
    
    # Add popularity column
    df = add_popularity_column(df, avg_score)
    
    # Step 4: Save the result
    print("\n[Step 4] Saving analysed data...")
    
    # Create data directory if it doesn't exist
    os.makedirs("data", exist_ok=True)
    
    # Save analysed data
    output_file = "data/trends_analysed.csv"
    success = save_analysed_data(df, output_file)
    
    if not success:
        print("Failed to save analysed data. Exiting.")
        return
    
    # Print additional insights
    print_summary_statistics(df)
    
    print(f"\nData analysis completed successfully! ✓")
    print(f"Final dataset shape: {df.shape}")
    print(f"New columns added: engagement, is_popular")

if __name__ == "__main__":
    main()
