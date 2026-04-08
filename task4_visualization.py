"""
TrendPulse - Task 4: Data Visualization with Matplotlib
=======================================================
Author : Vishnu Vardhan Vemula
Date   : 2026-04-08

What this script does:
  1. Loads the analysed CSV data from Task 3
  2. Creates 3 different visualization charts using Matplotlib
  3. Generates individual chart files and a combined dashboard
  4. Saves all visualizations as PNG files for presentation

Input:  data/trends_analysed.csv (from Task 3)
Output: outputs/ folder with 4 PNG files (3 charts + 1 dashboard)
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

# Set matplotlib style for better-looking plots
plt.style.use('default')
plt.rcParams['figure.facecolor'] = 'white'
plt.rcParams['axes.facecolor'] = 'white'

def load_analysed_data(filepath):
    """
    Load the analysed CSV data into a Pandas DataFrame.
    Returns DataFrame if successful, None otherwise.
    """
    try:
        df = pd.read_csv(filepath)
        print(f"Loaded data: {df.shape[0]} stories, {df.shape[1]} columns")
        return df
    except FileNotFoundError:
        print(f"Error: File {filepath} not found!")
        return None
    except Exception as e:
        print(f"Error loading data: {e}")
        return None

def create_outputs_folder():
    """
    Create the outputs folder if it doesn't exist.
    """
    if not os.path.exists('outputs'):
        os.makedirs('outputs')
        print("Created outputs/ directory")
    else:
        print("outputs/ directory already exists")

def shorten_title(title, max_length=50):
    """
    Shorten title to max_length characters, adding '...' if truncated.
    """
    if len(title) <= max_length:
        return title
    return title[:max_length-3] + "..."

def create_top_stories_chart(df, output_path):
    """
    Create Chart 1: Top 10 Stories by Score (horizontal bar chart).
    """
    print("Creating Chart 1: Top 10 Stories by Score...")
    
    # Sort by score and get top 10
    top_stories = df.nlargest(10, 'score').copy()
    
    # Shorten titles for better display
    top_stories['short_title'] = top_stories['title'].apply(shorten_title)
    
    # Create figure
    plt.figure(figsize=(12, 8))
    
    # Create horizontal bar chart
    bars = plt.barh(range(len(top_stories)), top_stories['score'], 
                    color='#2E86AB', edgecolor='#1E5F8E', linewidth=0.5)
    
    # Customize the chart
    plt.yticks(range(len(top_stories)), top_stories['short_title'])
    plt.xlabel('Score (Upvotes)', fontsize=12, fontweight='bold')
    plt.title('Top 10 Stories by Score', fontsize=16, fontweight='bold', pad=20)
    
    # Add value labels on bars
    for i, (bar, score) in enumerate(zip(bars, top_stories['score'])):
        plt.text(bar.get_width() + 20, bar.get_y() + bar.get_height()/2, 
                f'{score:,}', ha='left', va='center', fontsize=10)
    
    # Adjust layout and save
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Saved: {output_path}")

def create_category_chart(df, output_path):
    """
    Create Chart 2: Stories per Category (bar chart).
    """
    print("Creating Chart 2: Stories per Category...")
    
    # Count stories per category
    category_counts = df['category'].value_counts()
    
    # Define colors for each category
    colors = {
        'technology': '#FF6B6B',
        'worldnews': '#4ECDC4', 
        'sports': '#45B7D1',
        'science': '#96CEB4',
        'entertainment': '#FFEAA7'
    }
    
    # Get colors for categories in order
    bar_colors = [colors.get(cat, '#95A5A6') for cat in category_counts.index]
    
    # Create figure
    plt.figure(figsize=(10, 6))
    
    # Create bar chart
    bars = plt.bar(category_counts.index, category_counts.values, 
                   color=bar_colors, edgecolor='black', linewidth=0.5)
    
    # Customize the chart
    plt.xlabel('Category', fontsize=12, fontweight='bold')
    plt.ylabel('Number of Stories', fontsize=12, fontweight='bold')
    plt.title('Stories per Category', fontsize=16, fontweight='bold', pad=20)
    
    # Add value labels on bars
    for bar, count in zip(bars, category_counts.values):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5, 
                str(count), ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    # Rotate x-axis labels for better readability
    plt.xticks(rotation=45, ha='right')
    
    # Adjust layout and save
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Saved: {output_path}")

def create_scatter_chart(df, output_path):
    """
    Create Chart 3: Score vs Comments (scatter plot).
    """
    print("Creating Chart 3: Score vs Comments...")
    
    # Separate popular and non-popular stories
    popular = df[df['is_popular'] == True]
    non_popular = df[df['is_popular'] == False]
    
    # Create figure
    plt.figure(figsize=(12, 8))
    
    # Create scatter plots
    plt.scatter(non_popular['score'], non_popular['num_comments'], 
               color='#FF6B6B', alpha=0.6, s=50, label='Not Popular', edgecolors='black', linewidth=0.5)
    plt.scatter(popular['score'], popular['num_comments'], 
               color='#4ECDC4', alpha=0.8, s=70, label='Popular', edgecolors='black', linewidth=0.5)
    
    # Customize the chart
    plt.xlabel('Score (Upvotes)', fontsize=12, fontweight='bold')
    plt.ylabel('Number of Comments', fontsize=12, fontweight='bold')
    plt.title('Score vs Comments by Popularity', fontsize=16, fontweight='bold', pad=20)
    plt.legend(fontsize=11)
    
    # Add grid for better readability
    plt.grid(True, alpha=0.3)
    
    # Use logarithmic scale if there are large values
    if df['score'].max() > 1000 or df['num_comments'].max() > 1000:
        plt.xscale('log')
        plt.yscale('log')
        plt.xlabel('Score (Upvotes) - Log Scale', fontsize=12, fontweight='bold')
        plt.ylabel('Number of Comments - Log Scale', fontsize=12, fontweight='bold')
    
    # Adjust layout and save
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Saved: {output_path}")

def create_dashboard(df, output_path):
    """
    Create bonus dashboard combining all 3 charts.
    """
    print("Creating Dashboard: Combined View...")
    
    # Create figure with subplots
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('TrendPulse Dashboard', fontsize=20, fontweight='bold', y=0.98)
    
    # Chart 1: Top Stories (smaller version)
    top_stories = df.nlargest(5, 'score').copy()  # Top 5 for dashboard
    top_stories['short_title'] = top_stories['title'].apply(lambda x: shorten_title(x, 40))
    
    ax1.barh(range(len(top_stories)), top_stories['score'], color='#2E86AB')
    ax1.set_yticks(range(len(top_stories)))
    ax1.set_yticklabels(top_stories['short_title'], fontsize=9)
    ax1.set_xlabel('Score', fontweight='bold')
    ax1.set_title('Top 5 Stories by Score', fontweight='bold')
    
    # Chart 2: Categories (smaller version)
    category_counts = df['category'].value_counts()
    colors_dict = {
        'technology': '#FF6B6B',
        'worldnews': '#4ECDC4', 
        'sports': '#45B7D1',
        'science': '#96CEB4',
        'entertainment': '#FFEAA7'
    }
    bar_colors = [colors_dict.get(cat, '#95A5A6') for cat in category_counts.index]
    
    bars = ax2.bar(category_counts.index, category_counts.values, color=bar_colors)
    ax2.set_xlabel('Category', fontweight='bold')
    ax2.set_ylabel('Stories', fontweight='bold')
    ax2.set_title('Stories per Category', fontweight='bold')
    ax2.tick_params(axis='x', rotation=45)
    
    # Add value labels
    for bar, count in zip(bars, category_counts.values):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3, 
                str(count), ha='center', va='bottom', fontweight='bold')
    
    # Chart 3: Scatter plot (smaller version)
    popular = df[df['is_popular'] == True]
    non_popular = df[df['is_popular'] == False]
    
    ax3.scatter(non_popular['score'], non_popular['num_comments'], 
               color='#FF6B6B', alpha=0.6, s=30, label='Not Popular')
    ax3.scatter(popular['score'], popular['num_comments'], 
               color='#4ECDC4', alpha=0.8, s=40, label='Popular')
    ax3.set_xlabel('Score', fontweight='bold')
    ax3.set_ylabel('Comments', fontweight='bold')
    ax3.set_title('Score vs Comments', fontweight='bold')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # Chart 4: Summary statistics
    ax4.axis('off')
    
    # Calculate summary stats
    total_stories = len(df)
    avg_score = df['score'].mean()
    avg_comments = df['num_comments'].mean()
    popular_count = df['is_popular'].sum()
    popular_pct = (popular_count / total_stories) * 100
    
    # Create summary text
    summary_text = f"""
    DATASET SUMMARY
    ═══════════════════════════
    
    Total Stories: {total_stories}
    Average Score: {avg_score:.0f}
    Average Comments: {avg_comments:.0f}
    
    Popular Stories: {popular_count} ({popular_pct:.1f}%)
    
    TOP CATEGORIES
    ═══════════════════════════
    """
    
    # Add top categories
    for i, (cat, count) in enumerate(category_counts.head(3).items()):
        pct = (count / total_stories) * 100
        summary_text += f"\n  {i+1}. {cat}: {count} ({pct:.1f}%)"
    
    ax4.text(0.1, 0.9, summary_text, transform=ax4.transAxes, 
            fontsize=11, verticalalignment='top', fontfamily='monospace')
    
    # Adjust layout and save
    plt.tight_layout()
    plt.subplots_adjust(top=0.93)
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Saved: {output_path}")

def main():
    """
    Main function to orchestrate the visualization creation process.
    """
    print("=" * 60)
    print("  TrendPulse – Task 4: Data Visualization with Matplotlib")
    print("=" * 60)
    print()
    
    # Step 1: Setup
    print("[Step 1] Loading data and setting up...")
    
    # Load data
    csv_file = "data/trends_analysed.csv"
    df = load_analysed_data(csv_file)
    
    if df is None:
        print("Failed to load data. Exiting.")
        return
    
    # Create outputs folder
    create_outputs_folder()
    
    print()
    
    # Step 2: Create individual charts
    print("[Step 2] Creating individual charts...")
    
    # Chart 1: Top Stories
    create_top_stories_chart(df, "outputs/chart1_top_stories.png")
    
    # Chart 2: Categories
    create_category_chart(df, "outputs/chart2_categories.png")
    
    # Chart 3: Scatter Plot
    create_scatter_chart(df, "outputs/chart3_scatter.png")
    
    print()
    
    # Step 3: Create dashboard (bonus)
    print("[Step 3] Creating dashboard...")
    create_dashboard(df, "outputs/dashboard.png")
    
    print()
    print("All visualizations created successfully! ✓")
    print()
    print("Files created:")
    print("  outputs/chart1_top_stories.png")
    print("  outputs/chart2_categories.png") 
    print("  outputs/chart3_scatter.png")
    print("  outputs/dashboard.png (bonus)")

if __name__ == "__main__":
    main()
