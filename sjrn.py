import pandas as pd
import csv
import re
from difflib import get_close_matches

COMBINED_FILE = "combined_journals_report.xlsx"
SCIMAGO_FILE = "scimagojr_2025_cleanx.csv"   # must be real CSV, not ZIP
OUTPUT_FILE = "combined_journals_with_SJR_FINAL.xlsx"

TITLE_COL = "Source title"
SCIMAGO_TITLE_COL = "Title"
SCIMAGO_QUARTILE_COL = "SJR Best Quartile"
SCIMAGO_HINDEX_COL = "H index"

def normalize(s):
    s = str(s).lower().strip()
    s = re.sub(r'[^\w\s]', ' ', s)   # remove punctuation
    s = re.sub(r'\s+', ' ', s)       # collapse spaces
    s = s.replace('&', 'and')
    return s.strip()

# ------------------------------------------------------------
# 1. Load your combined report
# ------------------------------------------------------------
combined_df = pd.read_excel(COMBINED_FILE)
combined_df["_norm"] = combined_df[TITLE_COL].apply(normalize)
print(f"Loaded {len(combined_df)} journals from combined report.")

# ------------------------------------------------------------
# 2. Read SCImago file robustly (real CSV only)
# ------------------------------------------------------------
scimago_dict = {}   # norm_title -> (quartile, hindex)

with open(SCIMAGO_FILE, 'r', encoding='latin1') as f:
    # sniff the delimiter: maybe comma or semicolon
    first_line = f.readline()
    f.seek(0)
    delimiter = ';' if ';' in first_line else ','
    
    reader = csv.reader(f, delimiter=delimiter, quotechar='"')
    header = next(reader)
    # Clean header (remove BOM, etc.)
    header = [h.strip().replace('\ufeff', '') for h in header]
    
    # Find column indices (case-insensitive)
    header_lower = [h.lower() for h in header]
    try:
        title_idx = header_lower.index(SCIMAGO_TITLE_COL.lower())
        quartile_idx = header_lower.index(SCIMAGO_QUARTILE_COL.lower())
        hindex_idx = header_lower.index(SCIMAGO_HINDEX_COL.lower())
    except ValueError as e:
        print("Available columns:", header)
        raise ValueError(f"Column not found: {e}")

    for row in reader:
        if len(row) != len(header):
            continue
        title = row[title_idx].strip()
        if not title:
            continue
        norm_title = normalize(title)
        quartile = row[quartile_idx].strip()
        hindex = row[hindex_idx].strip()
        try:
            hindex = int(float(hindex))
        except:
            pass
        if norm_title not in scimago_dict:
            scimago_dict[norm_title] = (quartile, hindex)

print(f"Loaded {len(scimago_dict)} unique normalized SCImago titles.")

# ------------------------------------------------------------
# 3. Match using exact + fallback to fuzzy (difflib)
# ------------------------------------------------------------
matched = []
for idx, row in combined_df.iterrows():
    norm = row["_norm"]
    if norm in scimago_dict:
        q, h = scimago_dict[norm]
    else:
        # fuzzy match: find best among scimago keys with similarity > 0.9
        close = get_close_matches(norm, scimago_dict.keys(), n=1, cutoff=0.9)
        if close:
            q, h = scimago_dict[close[0]]
        else:
            q, h = "Not found", "Not found"
    matched.append((q, h))

combined_df["SJR Quartile"] = [m[0] for m in matched]
combined_df["SJR H-index"] = [m[1] for m in matched]
combined_df.drop(columns=["_norm"], inplace=True)

combined_df.to_excel(OUTPUT_FILE, index=False)
print(f"\nSaved to {OUTPUT_FILE}")
matched_count = (combined_df["SJR Quartile"] != "Not found").sum()
print(f"Matched: {matched_count} out of {len(combined_df)}")