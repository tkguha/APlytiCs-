import pandas as pd

# ============================================
# CONFIGURATION - EDIT THESE LINES
# ============================================
INSTITUTE_NAME = "Indian Institute of Technology Guwahati"
INPUT_CSV_FILE = "scopus_export.csv"  # Change to your file name
OUTPUT_CSV_FILE = "filtered_articles.csv"
OUTPUT_SUMMARY_FILE = "publisher_summary.csv"
# ============================================

def is_corresponding_author_from_institute(correspondence_address):
    """Check if correspondence address contains institute name."""
    if pd.isna(correspondence_address) or not isinstance(correspondence_address, str):
        return False
    
    addr_lower = correspondence_address.lower()
    
    institute_variations = [
        INSTITUTE_NAME.lower(),
        "iit guwahati",
        "iitg",
        "indian institute of technology guwahati"
    ]
    
    for variation in institute_variations:
        if variation in addr_lower:
            return True
    
    return False

def is_gold_or_hybrid_oa(oa_string):
    """
    Check if the OA cell contains 'Gold Open Access' OR 'Hybrid Gold Open Access'.
    Handles multiple values separated by semicolons.
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
    if "All Open Access" in oa_string:
        # This is a meta-label, not a specific OA type
        pass
    
    if not types:
        return oa_string[:50]  # Return first 50 chars if no match
    
    return " + ".join(types)

def extract_corresponding_author_name(correspondence_address):
    """Extract name of corresponding author."""
    if pd.isna(correspondence_address) or not isinstance(correspondence_address, str):
        return ""
    
    first_part = correspondence_address.split(';')[0].strip()
    
    if 'email:' in first_part.lower():
        first_part = first_part.split('email:')[0].strip()
    
    return first_part

def main():
    print("="*60)
    print("SCOPUS OA FILTER - GOLD/HYBRID ONLY")
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
    
    # Check required columns
    required_columns = ['Correspondence Address', 'Open Access']
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        print(f"❌ Error: Missing columns: {missing_columns}")
        print("Available columns:", list(df.columns))
        return
    
    # Step 1: Identify Gold/Hybrid OA (handling multiple values in one cell)
    print("\n📊 Step 1: Analyzing Open Access types...")
    df['Is_Gold_or_Hybrid'] = df['Open Access'].apply(is_gold_or_hybrid_oa)
    df['OA_Type_Label'] = df['Open Access'].apply(get_oa_type_label)
    
    gold_hybrid_count = df['Is_Gold_or_Hybrid'].sum()
    
    # Show breakdown of OA types in your data
    print(f"\n  Total articles: {len(df)}")
    print(f"  ✅ Gold OR Hybrid OA articles: {gold_hybrid_count}")
    print(f"  ❌ Green-only articles: {len(df) - gold_hybrid_count}")
    
    # Show distribution of OA types
    print("\n  OA Type distribution in your data:")
    oa_dist = df['OA_Type_Label'].value_counts()
    for oa_type, count in oa_dist.head(10).items():
        print(f"    - {oa_type}: {count} articles")
    
    # Step 2: Identify corresponding author from institute
    print("\n📊 Step 2: Identifying corresponding authors from institute...")
    df['Corresponding_Author_From_Institute'] = df['Correspondence Address'].apply(
        is_corresponding_author_from_institute
    )
    corr_author_count = df['Corresponding_Author_From_Institute'].sum()
    print(f"  Articles with corresponding author from {INSTITUTE_NAME}: {corr_author_count}")
    
    # Step 3: Apply BOTH filters
    df['Corresponding_Author_Name'] = df['Correspondence Address'].apply(
        extract_corresponding_author_name
    )
    
    # Final filter: Gold/Hybrid AND Corresponding author from institute
    final_filtered = df[
        (df['Is_Gold_or_Hybrid'] == True) & 
        (df['Corresponding_Author_From_Institute'] == True)
    ].copy()
    
    print("\n" + "="*60)
    print("FILTERING SUMMARY")
    print("="*60)
    print(f"Total articles in export:                         {len(df)}")
    print(f"After Gold/Hybrid filter (any article with Gold/Hybrid):  {gold_hybrid_count}")
    print(f"After Corresponding Author filter:                 {corr_author_count}")
    print(f"✅ After BOTH filters (FINAL - QUALIFYING):        {len(final_filtered)}")
    
    if len(final_filtered) == 0:
        print("\n⚠️ WARNING: No articles match both criteria!")
        print("\nDiagnostic - What got excluded?")
        
        only_gold_not_corr = df[
            (df['Is_Gold_or_Hybrid'] == True) & 
            (df['Corresponding_Author_From_Institute'] == False)
        ]
        only_corr_not_gold = df[
            (df['Is_Gold_or_Hybrid'] == False) & 
            (df['Corresponding_Author_From_Institute'] == True)
        ]
        
        print(f"  • Gold/Hybrid BUT corresponding author NOT from institute: {len(only_gold_not_corr)}")
        print(f"  • Corresponding author from institute BUT not Gold/Hybrid: {len(only_corr_not_gold)}")
        
        # Show sample of excluded Gold/Hybrid articles (to check if institute name is correct)
        if len(only_gold_not_corr) > 0:
            print("\n  Sample of Gold/Hybrid articles where corresponding author is NOT from your institute:")
            for idx, row in only_gold_not_corr.head(3).iterrows():
                corr_addr = str(row['Correspondence Address'])[:100]
                print(f"    - {corr_addr}...")
        
        return
    
    # Save results
    final_filtered.to_csv(OUTPUT_CSV_FILE, index=False, encoding='utf-8')
    print(f"\n💾 Saved filtered articles to: {OUTPUT_CSV_FILE}")
    
    # Publisher-wise summary
    if 'Publisher' in final_filtered.columns:
        publisher_summary = final_filtered.groupby('Publisher').size().reset_index(name='Article_Count')
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
    if 'Year' in final_filtered.columns:
        print("\n" + "="*60)
        print("YEAR-WISE BREAKDOWN (Gold/Hybrid OA only)")
        print("="*60)
        year_summary = final_filtered.groupby('Year').size().sort_index(ascending=False)
        for year, count in year_summary.items():
            print(f"  {year}: {count} articles")
    
    # Sample output
    print("\n" + "="*60)
    print("📄 SAMPLE OF QUALIFYING ARTICLES (first 5)")
    print("="*60)
    for idx, row in final_filtered.head(5).iterrows():
        title = row.get('Title', 'N/A')[:70]
        corr_author = row['Corresponding_Author_Name']
        oa_label = row['OA_Type_Label']
        publisher = row.get('Publisher', 'N/A')
        print(f"\n  ✉️  Corresponding author: {corr_author}")
        print(f"     📝 Title: {title}...")
        print(f"     📚 Publisher: {publisher}")
        print(f"     🔓 OA Type: {oa_label}")

if __name__ == "__main__":
    main()