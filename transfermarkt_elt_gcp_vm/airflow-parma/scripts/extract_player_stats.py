import aiohttp
from aiohttp.client_exceptions import ClientPayloadError, ClientError
from aiohttp import ClientSession, ClientTimeout
import asyncio
from bs4 import BeautifulSoup
import pandas as pd
import os
import time
import sys
import validation as va

output_name = sys.argv[1]

MAX_RETRIES = 5

async def fetch(session: ClientSession, url: str) -> str:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }
    for i in range(MAX_RETRIES):
        try:
            async with session.get(url, headers=headers, timeout=ClientTimeout(total=60)) as response:
                data = await response.read()
                return data.decode('utf-8', errors='ignore')
        except ClientPayloadError:
            continue
        except asyncio.TimeoutError:
            print(f"Timeout error on attempt {i+1} for {url}")
        except ClientError as e:
            print(f"Client error {e} on attempt {i+1} for {url}")
        except Exception as e:
            print(f"Unexpected error {e} on attempt {i+1} for {url}")
        await asyncio.sleep(1)  # delay between retries
    raise Exception(f"Failed to fetch {url} after {MAX_RETRIES} attempts")

from bs4 import BeautifulSoup

async def process_player(session, player_id, processed_ids, all_data):
    # Skip player if already processed
    if player_id in processed_ids:
        return

    url = f'https://www.transfermarkt.com/kylian-mbappe/leistungsdatendetails/spieler/{player_id}/plus/0?saison='
    html = await fetch(session, url)
    soup = BeautifulSoup(html, 'html.parser')

    # Find all table rows
    rows = soup.find_all('tr')

    try:
        # Find all 'th' elements
        header_elements = soup.find('thead').find_all('th')

        # Define the fields you are interested in
        fields = [
            "Season",
            "Appearances",
            "Goals",
            "Assists",
            "Yellow cards",
            "Second yellow cards",
            "Red cards",
            "Minutes played"
        ]

        # Initialize a dictionary to store the column numbers
        column_numbers = {}

        # Iterate over the header elements
        for i, element in enumerate(header_elements):
            # Get the text inside the current 'th' element
            text = element.get_text(strip=True)

            # If the text is in the fields list, store its index
            if text in fields:
                column_numbers[text] = i

            # If the text is not in the fields list, check the 'title' attribute of the 'span' tag inside the 'th' element
            else:
                span = element.find('span')
                if span and span.get('title') in fields:
                    column_numbers[span.get('title')] = i

        # Iterate over rows skipping the header row
        for row in rows[1:]:
            # Extract data from each row
            columns = row.find_all('td')

            # Check if there are enough columns
            if len(columns) >= 9:

                try:
                    season = columns[column_numbers['Season']].get_text(strip=True)
                except (ValueError, KeyError):
                    season = None
            
                try:
                    appearances = int(columns[column_numbers['Appearances']].get_text(strip=True))
                except (ValueError, KeyError):
                    appearances = None

                try:
                    goals = int(columns[column_numbers['Goals']].get_text(strip=True))
                except (ValueError, KeyError):
                    goals = None

                try:
                    assists = int(columns[column_numbers['Assists']].get_text(strip=True))
                except (ValueError, KeyError):
                    assists = None
                try:
                    cards = columns[column_numbers['Yellow cards']].get_text(strip=True).split('/')
                    yellow_cards = None if not cards[0].strip().isdigit() else int(cards[0])                  
                    second_yellow_cards = None if len(cards) < 2 or not cards[1].strip().isdigit() else int(cards[1])
                    red_cards = None if len(cards) < 3 or not cards[2].strip().isdigit() else int(cards[2])
                except (ValueError, KeyError):
                    yellow_cards = None
                    second_yellow_cards = None
                    red_cards = None

                minutes_element = row.find('td', class_='rechts')
                if minutes_element:
                    try:
                        minutes = float(minutes_element.get_text(strip=True).replace("'", ""))
                    except (ValueError, KeyError):
                        minutes = None
                else:
                    minutes = None

                # Append data to the list
                all_data.append({
                    "Player ID": player_id,
                    "Season": season,
                    "Appearances": appearances,
                    "Goals": goals,
                    "Assists": assists,
                    "Yellow Cards": yellow_cards,
                    "Second Yellow Cards": second_yellow_cards,
                    "Red Cards": red_cards,
                    "Minutes": minutes
                })
    except AttributeError:
        all_data.append({
        "Player ID": player_id,
        "Season": None,
        "Appearances": None,
        "Goals": None,
        "Assists": None,
        "Yellow Cards": None,
        "Second Yellow Cards": None,
        "Red Cards": None,
        "Minutes": None
        })
        

    # Add player_id to processed_ids and write it to the file
    processed_ids.add(player_id)


async def main():
    # Read player_ids from CSV file
    df_players = pd.read_csv(f'/tmp/{output_name}-profiles-cleaned.csv')

    player_ids = df_players['player_id'].unique()

    # Create a list to store all data
    all_data = []

    # Create a set to keep track of processed ids
    processed_ids = set()

    # Read processed_ids from text file
    try:
        with open(f'/tmp/{output_name}-stats-processed-urls.txt', 'r') as f:
            processed_ids = set(line.strip() for line in f)
    except FileNotFoundError:
        pass

    async with aiohttp.ClientSession() as session:
        tasks = []
        for i, player_id in enumerate(player_ids):
            task = process_player(session, player_id, processed_ids, all_data)
            tasks.append(task)
            if (i + 1) % 1000 == 0:
                await asyncio.gather(*tasks)
                tasks = []
                # Create a DataFrame from the list
                df = pd.DataFrame(all_data)

                # Group the data by Player ID and Season, and sum the other columns
                df_grouped = df.groupby(['Player ID', 'Season']).sum().reset_index()

                # Pivot the DataFrame to get one row per player and one column per season for each statistic
                df_pivot = df_grouped.pivot(index='Player ID', columns='Season')

                # Flatten the MultiIndex columns
                df_pivot.columns = [' '.join(col).strip() for col in df_pivot.columns.values]

                # Reset the index
                df_pivot.reset_index(inplace=True)

                # Check if the file exists
                file_exists = os.path.isfile(f'/tmp/{output_name}-player_stats.csv')

                # Write the DataFrame to a CSV file
                df_pivot.to_csv(f'/tmp/{output_name}-player_stats.csv', mode='w+', header=True, index=False)

                # Write processed_ids to a text file
                with open(f'/tmp/{output_name}-stats-processed-urls.txt', 'w+') as f:
                    for id in processed_ids:
                        f.write(f'{id}\n')
                        
                #all_data.clear()
        if tasks:  # If there are remaining tasks, await them
            await asyncio.gather(*tasks)

    # Save remaining data to CSV
    df = pd.DataFrame(all_data)
    df.to_csv(f'/tmp/{output_name}-player_stats.csv', mode='w+', header=True, index=False)

    # Save remaining processed_ids to file
    with open(f'/tmp/{output_name}-stats-processed-urls.txt', 'w+') as f:
        for id in processed_ids:
            f.write(f'{id}\n')


if __name__ == "__main__":
    try:
        va.validate_input(output_name)
        start_time = time.time()
        asyncio.run(main())
        end_time = time.time()
        print(f"Time taken: {end_time - start_time} seconds")
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)

