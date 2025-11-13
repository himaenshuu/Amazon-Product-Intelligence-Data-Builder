import json
import os

# Load the JSON file
input_file = 'amazon_results.json'
output_file = 'amazon_results_cleaned.json'

print(f" Loading {input_file}...")
with open(input_file, 'r', encoding='utf-8') as f:
    records = json.load(f)

print(f"Total records before cleaning: {len(records)}")

# Separate records with and without errors
valid_records = []
error_records = []

for record in records:
    if 'error' in record:
        error_records.append(record)
    else:
        valid_records.append(record)

# Print statistics
print(f"\n Statistics:")
print(f" Valid records: {len(valid_records)}")
print(f" Records with errors: {len(error_records)}")

# Show error details
if error_records:
    print(f"\nASINs with errors:")
    for record in error_records:
        asin = record.get('asin', 'Unknown')
        error = record.get('error', 'Unknown error')
        print(f"   • {asin}: {error[:80]}...")

# Save cleaned file
print(f"\nSaving cleaned data to {output_file}...")
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(valid_records, f, ensure_ascii=False, indent=4)

print(f"Cleaned file saved!")
print(f"Total records in cleaned file: {len(valid_records)}")

# Optional: Backup original file
backup_file = 'amazon_results_new_backup.json'
if not os.path.exists(backup_file):
    with open(backup_file, 'w', encoding='utf-8') as f:
        json.dump(records, f, ensure_ascii=False, indent=4)
    print(f"Backup created: {backup_file}")
