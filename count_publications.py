import csv
from collections import Counter

def count_years(csv_file, output_file):
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        years = [row['Year'] for row in reader if row['Year'].isdigit()]
    counter = Counter(years)
    with open(output_file, 'w', newline='') as out:
        writer = csv.writer(out)
        writer.writerow(['Year', 'Count'])
        for year in sorted(counter.keys()):
            writer.writerow([year, counter[year]])
    print(f"Saved {output_file}")

count_years('gold_hybrid_articles.csv', 'gold_hybrid_year_counts.csv')
count_years('filtered_articles.csv', 'filtered_year_counts.csv')