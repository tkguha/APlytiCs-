import pandas as pd

# Load the Excel file
file_path = "filtered_journals.xlsx"  # Update path if needed
df = pd.read_excel(file_path, sheet_name="filtered_journals")

# Count frequency of each source title
frequency = df["Source title"].value_counts().reset_index()
frequency.columns = ["Source title", "Frequency"]

# Print to console
print(frequency.to_string(index=False))

# Save to CSV
frequency.to_csv("source_title_frequency.csv", index=False)
print("\nFrequency table saved to 'source_title_frequency.csv'")