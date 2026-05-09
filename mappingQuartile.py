import pandas as pd
import csv

# ------------------------------
# CONFIGURATION
# ------------------------------
JOURNALS_FILE = "journal_frequency_report.xlsx"  # your journals file (with Article_Count, Publisher)
CITESCORE_FILE = "CiteScore 2024 annual values.csv"           # large Scopus file
OUTPUT_FILE = "journals_with_quartiles.csv"

ENCODING = 'latin1'   # for CiteScore file

JOURNAL_TITLE_COL = "Source title"
ARTICLE_COUNT_COL = "Article_Count"
PUBLISHER_COL = "Publisher"

CITESCORE_TITLE_COL = "Title"
QUARTILE_COL = "Quartile"
SUBJECT_COL = "Scopus Sub-Subject Area"

# ------------------------------
# 1. Load your journal list with all columns
# ------------------------------
if JOURNALS_FILE.endswith('.xlsx'):
    journals_df = pd.read_excel(JOURNALS_FILE)
else:
    journals_df = pd.read_csv(JOURNALS_FILE)

# Keep original data for merging later
original_journals = journals_df[[JOURNAL_TITLE_COL, ARTICLE_COUNT_COL, PUBLISHER_COL]].copy()
original_journals["normalized"] = original_journals[JOURNAL_TITLE_COL].str.lower().str.strip()

# For matching, use unique titles
unique_titles = original_journals[[JOURNAL_TITLE_COL, "normalized"]].drop_duplicates(subset="normalized")
journal_titles_norm = set(unique_titles["normalized"])
title_to_original = dict(zip(unique_titles["normalized"], unique_titles[JOURNAL_TITLE_COL]))

print(f"Loaded {len(journal_titles_norm)} unique journal titles from {JOURNALS_FILE}")

# ------------------------------
# 2. Determine delimiter for CiteScore file
# ------------------------------
with open(CITESCORE_FILE, 'r', encoding=ENCODING) as f:
    first_line = f.readline()
    try:
        dialect = csv.Sniffer().sniff(first_line)
        delimiter = dialect.delimiter
    except:
        delimiter = '\t' if ',' not in first_line else ','
print(f"Using delimiter: '{delimiter}'")

# ------------------------------
# 3. Process CiteScore file in chunks
# ------------------------------
matched_data = []
chunk_size = 50000

try:
    reader = pd.read_csv(CITESCORE_FILE, sep=delimiter, encoding=ENCODING,
                         engine='c', chunksize=chunk_size, on_bad_lines='skip')
except:
    print("Falling back to 'python' engine (slower but more robust)")
    reader = pd.read_csv(CITESCORE_FILE, sep=delimiter, encoding=ENCODING,
                         engine='python', chunksize=chunk_size, on_bad_lines='skip')

for i, chunk in enumerate(reader):
    chunk["norm_title"] = chunk[CITESCORE_TITLE_COL].astype(str).str.lower().str.strip()
    mask = chunk["norm_title"].isin(journal_titles_norm)
    matches = chunk.loc[mask]
    
    for _, row in matches.iterrows():
        matched_data.append({
            "normalized_title": row["norm_title"],
            "Journal Title": title_to_original[row["norm_title"]],
            "Matched Title (CiteScore)": row[CITESCORE_TITLE_COL],
            "Quartile": row.get(QUARTILE_COL, ""),
            "Subject Area": row.get(SUBJECT_COL, "")
        })
    
    if (i+1) % 10 == 0:
        print(f"Processed {i+1} chunks, found {len(matched_data)} matches so far...")

print(f"Found {len(matched_data)} raw matches (multiple per journal possible).")

if not matched_data:
    print("No matches found. Check column names and title normalization.")
    exit()

# ------------------------------
# 4. Aggregate quartiles per journal
# ------------------------------
result_df = pd.DataFrame(matched_data)

def aggregate_quartiles(group):
    quartiles = group["Quartile"].dropna().unique()
    quartiles_str = []
    for q in quartiles:
        q_str = str(q).strip().upper()
        if q_str.startswith('Q'):
            quartiles_str.append(q_str)
        elif q_str.isdigit() and 1 <= int(q_str) <= 4:
            quartiles_str.append(f"Q{q_str}")
    if quartiles_str:
        quartiles_str.sort()
        best = quartiles_str[0]
        all_q = ", ".join(quartiles_str)
    else:
        best = "Unknown"
        all_q = "Unknown"
    subjects = ", ".join(group["Subject Area"].dropna().unique())
    return pd.Series({
        "Best Quartile": best,
        "All Quartiles": all_q,
        "Subjects (sample)": subjects[:200]
    })

quartile_summary = result_df.groupby("normalized_title").apply(aggregate_quartiles).reset_index()
# Rename normalized_title back to something we can merge on
quartile_summary = quartile_summary.rename(columns={"normalized_title": "normalized"})

# ------------------------------
# 5. Merge with original journal data (including Publisher and Article_Count)
# ------------------------------
# Keep one row per normalized title from original data (with first publisher & count – but all same per title)
original_unique = original_journals.drop_duplicates(subset="normalized")

final_df = original_unique.merge(quartile_summary, on="normalized", how="left")

# Select and order columns
final_output = final_df[[
    JOURNAL_TITLE_COL,
    ARTICLE_COUNT_COL,
    PUBLISHER_COL,
    "Best Quartile",
    "All Quartiles",
    "Subjects (sample)"
]]

# Sort by article count descending (optional)
final_output = final_output.sort_values(ARTICLE_COUNT_COL, ascending=False)

# Save
final_output.to_csv(OUTPUT_FILE, index=False)
print(f"\nResults saved to {OUTPUT_FILE}")
print("\nFirst 10 rows of output:")
print(final_output.head(10))