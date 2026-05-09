import pandas as pd
import csv

# ------------------------------
# CONFIGURATION
# ------------------------------
JOURNALS_FILE = "source_title_frequency_with_publisher.xlsx"  # your journals file
CITESCORE_FILE = "CiteScore 2024 annual values.csv"           # large Scopus file
OUTPUT_FILE = "journals_with_quartiles.csv"

# Force a universal encoding that handles any byte
ENCODING = 'latin1'   # or 'cp1252', 'iso-8859-1'

JOURNAL_TITLE_COL = "Source title"
CITESCORE_TITLE_COL = "Title"
QUARTILE_COL = "Quartile"
SUBJECT_COL = "Scopus Sub-Subject Area"

# ------------------------------
# 1. Load your journal list
# ------------------------------
if JOURNALS_FILE.endswith('.xlsx'):
    journals_df = pd.read_excel(JOURNALS_FILE)
else:
    journals_df = pd.read_csv(JOURNALS_FILE)

journals_df = journals_df[[JOURNAL_TITLE_COL]].drop_duplicates()
journals_df["normalized"] = journals_df[JOURNAL_TITLE_COL].str.lower().str.strip()
journal_titles_norm = set(journals_df["normalized"])
title_to_original = dict(zip(journals_df["normalized"], journals_df[JOURNAL_TITLE_COL]))
print(f"Loaded {len(journal_titles_norm)} unique journal titles from {JOURNALS_FILE}")

# ------------------------------
# 2. Determine delimiter
# ------------------------------
with open(CITESCORE_FILE, 'r', encoding=ENCODING) as f:
    first_line = f.readline()
    # Try to sniff delimiter
    try:
        dialect = csv.Sniffer().sniff(first_line)
        delimiter = dialect.delimiter
    except:
        # Fallback: tab if ',' not present, else comma
        delimiter = '\t' if ',' not in first_line else ','
print(f"Using delimiter: '{delimiter}'")

# ------------------------------
# 3. Process CiteScore file in chunks
# ------------------------------
matched_data = []
chunk_size = 50000  # larger chunk for speed

# Use 'c' engine for performance (requires consistent quoting)
# If errors occur, fallback to 'python' engine
try:
    reader = pd.read_csv(CITESCORE_FILE, sep=delimiter, encoding=ENCODING,
                         engine='c', chunksize=chunk_size, on_bad_lines='skip')
except:
    print("Falling back to 'python' engine (slower but more robust)")
    reader = pd.read_csv(CITESCORE_FILE, sep=delimiter, encoding=ENCODING,
                         engine='python', chunksize=chunk_size, on_bad_lines='skip')

for i, chunk in enumerate(reader):
    # Normalize titles
    chunk["norm_title"] = chunk[CITESCORE_TITLE_COL].astype(str).str.lower().str.strip()
    mask = chunk["norm_title"].isin(journal_titles_norm)
    matches = chunk.loc[mask]
    
    for _, row in matches.iterrows():
        matched_data.append({
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
# 4. Aggregate per journal
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

summary = result_df.groupby("Journal Title").apply(aggregate_quartiles).reset_index()
summary.to_csv(OUTPUT_FILE, index=False)
print(f"\nResults saved to {OUTPUT_FILE}")
print("\nFirst 10 matches:")
print(summary.head(10))