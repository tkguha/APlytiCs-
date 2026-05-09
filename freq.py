import pandas as pd

# Load the Excel file
file_path = "filtered_journals.xlsx"  # Update path if needed
df = pd.read_excel(file_path, sheet_name="filtered_journals")

# Group by Source title, count frequency, and take the first Publisher
# (assuming all rows for the same title have the same publisher)
frequency_df = df.groupby("Source title").agg(
    Frequency=("Source title", "count"),
    Publisher=("Publisher", "first")
).reset_index()

# Optional: check if any source title has multiple different publishers
multiple_publishers = df.groupby("Source title")["Publisher"].nunique()
inconsistent = multiple_publishers[multiple_publishers > 1]
if not inconsistent.empty:
    print("Warning: The following source titles have inconsistent publishers:")
    print(inconsistent.to_string())
    print("Using the first publisher encountered for each.\n")

# Rename column for clarity
frequency_df.rename(columns={"Source title": "Source title"}, inplace=True)

# Sort by frequency descending
frequency_df = frequency_df.sort_values("Frequency", ascending=False)

# Print to console
print(frequency_df.to_string(index=False))

# Save to CSV
frequency_df.to_csv("source_title_frequency_with_publisher.csv", index=False)
print("\nFrequency table saved to 'source_title_frequency_with_publisher.csv'")