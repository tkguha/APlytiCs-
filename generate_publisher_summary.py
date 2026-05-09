import pandas as pd

# ============================================
# CONFIGURATION
# ============================================
INPUT_FILE = "combined_journals_with_SJR_FINAL.xlsx"   # your Excel file
OUTPUT_FILE = "publisher_summary_from_combined.csv"   # output CSV
# ============================================

def main():
    # Read the Excel file (first sheet)
    try:
        df = pd.read_excel(INPUT_FILE, engine='openpyxl')
        print(f"✅ Loaded {len(df)} rows from {INPUT_FILE}")
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return
    
    # Check required columns
    if 'Publisher' not in df.columns or 'Article_Count' not in df.columns:
        print("❌ Required columns 'Publisher' or 'Article_Count' not found.")
        print("Available columns:", list(df.columns))
        return
    
    # Group by Publisher and sum Article_Count
    summary = df.groupby('Publisher', as_index=False)['Article_Count'].sum()
    
    # Sort descending by Article_Count
    summary = summary.sort_values('Article_Count', ascending=False)
    
    # Save to CSV
    summary.to_csv(OUTPUT_FILE, index=False)
    print(f"\n✅ Publisher summary saved to: {OUTPUT_FILE}")
    
    # Print first 20 rows to console
    print("\n" + "="*60)
    print("PUBLISHER SUMMARY (Top 20)")
    print("="*60)
    print(summary.head(20).to_string(index=False))
    
    print(f"\n📊 Total articles: {summary['Article_Count'].sum()}")
    print(f"📊 Total unique publishers: {len(summary)}")

if __name__ == "__main__":
    main()