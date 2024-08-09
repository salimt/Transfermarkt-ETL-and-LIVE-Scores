import pandas as pd
import sys
output_name = sys.argv[1]

# File paths to be cleaned
file_paths = [
    f'/tmp/{output_name}-market.csv',
]

# Output file paths for cleaned files
output_file_paths = [
    f'/tmp/{output_name}-market-cleaned.csv',
]

# Define the headers
headers = ['Club', 'Age', 'player_id', 'MarketValueAmount', 'Currency', 'Date', 'HighestMarketValue', 'HighestMarketValueDate', 'LastChangeDate']

# Iterate over each file path
for file_path, output_file_path in zip(file_paths, output_file_paths):
    # Load the data into a pandas DataFrame, adding the headers
    df = pd.read_csv(file_path, header=None, names=headers)

    # # Convert all date columns to datetime and remove the time component
    for column in ['Date', 'HighestMarketValueDate', 'LastChangeDate']:
        df[column] = pd.to_datetime(df[column], errors='coerce').dt.date.replace(pd.NaT, None)

    # Write the cleaned data to a new CSV file
    df.to_csv(output_file_path, index=False)