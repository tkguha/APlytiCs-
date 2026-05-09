import pandas as pd

# ------------------------------
# CONFIGURATION
# ------------------------------
FREQ_FILE = "source_title_frequency_with_publisher.xlsx"
QUARTILE_FILE = "journals_with_quartiles.csv"
OUTPUT_FILE = "combined_journals_report.xlsx"  # or .csv

# Column names
FREQ_TITLE_COL = "Source title"
QUARTILE_TITLE_COL = "Journal Title"

# ------------------------------
# 1. Load files
# ------------------------------
freq_df = pd.read_excel(FREQ_FILE)
quartile_df = pd.read_csv(QUARTILE_FILE)

# Normalize titles for merging (lowercase, strip spaces)
freq_df["_norm_title"] = freq_df[FREQ_TITLE_COL].str.lower().str.strip()
quartile_df["_norm_title"] = quartile_df[QUARTILE_TITLE_COL].str.lower().str.strip()

# ------------------------------
# 2. Merge (left join) – keep all journals from frequency file
# ------------------------------
merged = freq_df.merge(
    quartile_df[[
        "_norm_title",
        "Best Quartile",
        "All Quartiles",
        "Subjects (sample)"
    ]],
    on="_norm_title",
    how="left"
)

# Drop the temporary normalization column
merged.drop(columns=["_norm_title"], inplace=True)

# Reorder columns for readability
cols = [FREQ_TITLE_COL, "Frequency", "Publisher", "Best Quartile", "All Quartiles", "Subjects (sample)"]
merged = merged[cols]

# Journals that were not matched will have NaN; replace with "Not found" or leave blank
merged["Best Quartile"] = merged["Best Quartile"].fillna("Not found")
merged["All Quartiles"] = merged["All Quartiles"].fillna("Not found")
merged["Subjects (sample)"] = merged["Subjects (sample)"].fillna("Not found")

# ------------------------------
# 3. Save output
# ------------------------------
if OUTPUT_FILE.endswith(".xlsx"):
    merged.to_excel(OUTPUT_FILE, index=False)
else:
    merged.to_csv(OUTPUT_FILE, index=False)

print(f"Combined report saved to {OUTPUT_FILE}")
print(f"Total journals in frequency file: {len(freq_df)}")
print(f"Journals successfully matched: {merged['Best Quartile'].ne('Not found').sum()}")