import pandas as pd

# ============================================
# CONFIGURATION - EDIT THESE LINES
# ============================================
INPUT_CSV_FILE = "scopus_export.csv"  # Change to your file name
OUTPUT_CSV_FILE = "gold_hybrid_articles.csv"
OUTPUT_SUMMARY_FILE = "publisher_summary_gold_hybrid.csv"
# ============================================

def is_gold_or_hybrid_oa(oa_string):
    """
    Check if the OA cell contains 'Gold Open Access' OR 'Hybrid Gold Open Access'.
    Handles multiple values separated by semicolons.
    Returns True if Gold or Hybrid is present, False otherwise.
    """
    if pd.isna(oa_string) or not isinstance(oa_string, str):
        return False
    
    # Check for Gold
    if "Gold Open Access" in oa_string:
        return True
    
    # Check for Hybrid
    if "Hybrid Gold Open Access" in oa_string:
        return True
    
    return False

def get_oa_type_label(oa_string):
    """
    Return a human-readable label of what OA types are present.
    """
    if pd.isna(oa_string) or not isinstance(oa_string, str):
        return "Unknown"
    
    types = []
    if "Gold Open Access" in oa_string:
        types.append("Gold")
    if "Hybrid Gold Open Access" in oa_string:
        types.append("Hybrid")
    if "Green Open Access" in oa_string:
        types.append("Green")
    
    if not types:
        return oa_string[:50]  # Return first 50 chars if no match
    
    return " + ".join(types)

def main():
    print("="*60)
    print("SCOPUS OA FILTER - GOLD/HYBRID ONLY (No Corresponding Author Filter)")
    print("="*60)
    print(f"\nReading file: {INPUT_CSV_FILE}")
    
    try:
        df = pd.read_csv(INPUT_CSV_FILE, encoding='utf-8')
        print(f"✅ Successfully loaded {len(df)} records")
    except FileNotFoundError:
        print(f"❌ Error: File '{INPUT_CSV_FILE}' not found!")
        print("Please make sure the file is in the same directory as this script.")
        return
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return
    
    # Check required column
    if 'Open Access' not in df.columns:
        print(f"❌ Error: 'Open Access' column not found!")
        print("Available columns:", list(df.columns))
        return
    
    # Step 1: Identify Gold/Hybrid OA
    print("\n📊 Analyzing Open Access types...")
    df['Is_Gold_or_Hybrid'] = df['Open Access'].apply(is_gold_or_hybrid_oa)
    df['OA_Type_Label'] = df['Open Access'].apply(get_oa_type_label)
    
    gold_hybrid_count = df['Is_Gold_or_Hybrid'].sum()
    
    # Show breakdown
    print(f"\n  Total articles: {len(df)}")
    print(f"  ✅ Gold OR Hybrid OA articles: {gold_hybrid_count}")
    print(f"  ❌ Green-only articles (excluded): {len(df) - gold_hybrid_count}")
    
    # Show distribution of OA types
    print("\n  OA Type distribution in your data:")
    oa_dist = df['OA_Type_Label'].value_counts()
    for oa_type, count in oa_dist.head(10).items():
        print(f"    - {oa_type}: {count} articles")
    
    # Filter to keep only Gold/Hybrid
    filtered_df = df[df['Is_Gold_or_Hybrid'] == True].copy()
    
    print("\n" + "="*60)
    print("FILTERING SUMMARY")
    print("="*60)
    print(f"Total articles in export:           {len(df)}")
    print(f"✅ Articles kept (Gold/Hybrid):     {len(filtered_df)}")
    print(f"❌ Articles excluded (Green only):  {len(df) - len(filtered_df)}")
    
    if len(filtered_df) == 0:
        print("\n⚠️ WARNING: No Gold or Hybrid OA articles found in your export!")
        print("Please check that your Scopus export includes Open Access articles.")
        print("\nFirst few unique OA values in your data:")
        unique_oa = df['Open Access'].dropna().unique()[:10]
        for val in unique_oa:
            print(f"  - {val}")
        return
    
    # Save results
    filtered_df.to_csv(OUTPUT_CSV_FILE, index=False, encoding='utf-8')
    print(f"\n💾 Saved Gold/Hybrid articles to: {OUTPUT_CSV_FILE}")
    
    # Publisher-wise summary
    if 'Publisher' in filtered_df.columns:
        publisher_summary = filtered_df.groupby('Publisher').size().reset_index(name='Article_Count')
        publisher_summary = publisher_summary.sort_values('Article_Count', ascending=False)
        publisher_summary.to_csv(OUTPUT_SUMMARY_FILE, index=False, encoding='utf-8')
        
        print(f"💾 Saved publisher summary to: {OUTPUT_SUMMARY_FILE}")
        
        print("\n" + "="*60)
        print("PUBLISHER-WISE SUMMARY (Gold/Hybrid OA only)")
        print("="*60)
        print(publisher_summary.to_string(index=False))
        
        # Also show as percentage
        total = publisher_summary['Article_Count'].sum()
        print(f"\n📊 Total qualifying articles: {total}")
        print("\nPublisher-wise percentage:")
        for _, row in publisher_summary.iterrows():
            pct = (row['Article_Count'] / total) * 100
            print(f"  {row['Publisher']}: {row['Article_Count']} ({pct:.1f}%)")
    
    # Year-wise breakdown
    if 'Year' in filtered_df.columns:
        print("\n" + "="*60)
        print("YEAR-WISE BREAKDOWN (Gold/Hybrid OA only)")
        print("="*60)
        year_summary = filtered_df.groupby('Year').size().sort_index(ascending=False)
        for year, count in year_summary.items():
            print(f"  {year}: {count} articles")
    
    # Sample output
    print("\n" + "="*60)
    print("📄 SAMPLE OF KEPT ARTICLES (first 5)")
    print("="*60)
    for idx, row in filtered_df.head(5).iterrows():
        title = row.get('Title', 'N/A')[:70]
        oa_label = row['OA_Type_Label']
        publisher = row.get('Publisher', 'N/A')
        print(f"\n  📝 Title: {title}...")
        print(f"     📚 Publisher: {publisher}")
        print(f"     🔓 OA Type: {oa_label}")

if __name__ == "__main__":
    main()