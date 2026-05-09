import pandas as pd

# ============================================
# CONFIGURATION - EDIT THE FILE PATH
# ============================================
file_path = "gold_hybrid_articles.xlsx"   # Your Excel file
# ============================================

def main():
    # Load the Excel file without specifying sheet name (reads first sheet)
    try:
        df = pd.read_excel(file_path, engine='openpyxl')
        print(f"✅ Loaded {len(df)} rows from the first sheet.")
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return
    
    # Verify required columns exist
    if 'Source title' not in df.columns or 'Publisher' not in df.columns:
        print("❌ Required columns 'Source title' or 'Publisher' not found.")
        print("Available columns:", list(df.columns))
        return
    
    # Group by journal and count frequency, take first publisher
    freq_df = df.groupby('Source title').agg(
        Article_Count=('Source title', 'count'),
        Publisher=('Publisher', 'first')
    ).reset_index()
    
    # Sort descending by count
    freq_df = freq_df.sort_values('Article_Count', ascending=False)
    
    # Print to console
    print("\n" + "="*60)
    print("JOURNAL FREQUENCY REPORT (Gold/Hybrid OA)")
    print("="*60)
    print(freq_df.to_string(index=False))
    
    # Save to CSV
    output_file = "journal_frequency_report.csv"
    freq_df.to_csv(output_file, index=False)
    print(f"\n✅ Report saved to: {output_file}")
    print(f"📊 Summary: {len(freq_df)} unique journals, {freq_df['Article_Count'].sum()} total articles.")

if __name__ == "__main__":
    main()