import csv
import sys

seen_player_ids = set()
output_name = sys.argv[1]
with open(f'/tmp/{output_name}-profiles.csv', 'r') as infile, \
     open(f'/tmp/{output_name}-profiles-cleaned.csv', 'w+', newline='') as outfile:
    reader = csv.reader(infile)
    writer = csv.writer(outfile)
    for row in reader:
        player_id = row[0]  # assuming player_id is the first column
        if player_id not in seen_player_ids:
            cleaned_row = [field.replace('\n', ' ') for field in row]
            writer.writerow(cleaned_row)
            seen_player_ids.add(player_id)