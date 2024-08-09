import requests
from datetime import datetime
import pandas as pd
import sys
from typing import List, Dict
import validation as va
import os
from concurrent.futures import ThreadPoolExecutor
from requests.exceptions import RequestException
import concurrent.futures


def main() -> None:
    """
    The main function of the script. It validates the output name, checks if the output file already exists, 
    and if not, it initiates a process to extract player information.

    :param output_name: The name of the output, passed as a command line argument.
    :param va: A module that contains the validate_input function.
    :param extract_player_info: A function that extracts player information.
    """
    output_name = sys.argv[1]
    try:
        va.validate_input(output_name)
        if os.path.exists(f'/tmp/{output_name}-market.csv'):
            print(f"File '/tmp/{output_name}-market.csv' already exists. Skipping scraping.")
            return
        else:
            with ThreadPoolExecutor() as executor:
                executor.submit(extract_player_info, output_name)
            time.sleep(0)
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        sys.exit(1)

# Extract player info
def extract_player_info(filename: str) -> None:
    """
    Extracts player information from the given URLs and saves it to a CSV file.

    Args:
        filename (str): The name of the file to save the extracted data.

    Raises:
        Exception: If an error occurs while extracting player info.

    Returns:
        None
    """
    try:     
        if os.path.exists(f'/tmp/{filename}-market-processed_ids.txt'):
            with open(f'/tmp/{filename}-market-processed_ids.txt', 'r') as f:
                processed_ids = set(line.strip() for line in f)
        else:
            processed_ids = set()
            with open(f'/tmp/{filename}-market-processed_ids.txt', 'w') as f:  # Create the file if it doesn't exist
                pass
     
        player_info_df = pd.read_csv(f'/tmp/{filename}-profiles-cleaned.csv')
        player_ids = player_info_df["player_id"].tolist()

        rows: List[Dict[str, any]] = []

        def process_player(session: requests.Session, player_id: str):
            """
            Fetches and processes player data from a given URL.

            Args:
                session (requests.Session): The session to use for making the HTTP request.
                player_id (str): The ID of the player to process.

            Returns:
                List[Dict[str, Optional[str]]]: A list of dictionaries containing the processed player data.
            """
            url = f"https://www.transfermarkt.com/ceapi/marketValueDevelopment/graph/{player_id}"
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36"
            }
            if player_id in processed_ids:
                return None
            try:
                response = session.get(url, headers=headers, allow_redirects=False)
                response.raise_for_status()
                data = response.json()
                market_values = data["list"] 
                highest_market_value = data["highest"] if data["highest"] != "-" else None
                highest_market_value_date = datetime.strptime(data["highest_date"], "%b %d, %Y").strftime("%Y-%m-%d") if data["highest_date"] != "-" else None
                last_change_date = datetime.strptime(data["last_change"], "%b %d, %Y").strftime("%Y-%m-%d") if data["last_change"] != "-" else None

                rows = []
                for item in market_values:
                    row = {
                        "Club": item["verein"],
                        "Age": int(item["age"]) if item["age"] != "-" else None,
                        "player_id": int(player_id),
                        "MarketValueAmount": parse_currency(item["mw"]) if item["mw"] != "-" else None,
                        "Currency": item["mw"][0],
                        "Date": datetime.strptime(item["datum_mw"], "%b %d, %Y") if item["datum_mw"] != "-" else None,
                        "HighestMarketValue": parse_currency(highest_market_value),
                        "HighestMarketValueDate": highest_market_value_date,
                        "LastChangeDate": last_change_date
                    }
                    rows.append(row)

                processed_ids.add(player_id)

                with open(f'/tmp/{filename}-market-processed_ids.txt', 'a') as f:
                    f.write(f'{player_id}\n')

                pd.DataFrame(rows).to_csv(f'/tmp/{filename}-market.csv', index=False, mode='a', header=not os.path.exists(f'/tmp/{filename}-market.csv'))

                return rows
            except RequestException as e:
                print(f"An error occurred while accessing {url}: {str(e)}")
                sys.exit(1)
            except Exception as e:
                print(f"An error occurred: {str(e)}")
                sys.exit(1)
                                
                        
        with requests.Session() as session:
            with ThreadPoolExecutor() as executor:
                tasks = {executor.submit(process_player, session, player_id) for player_id in player_ids}
                for future in concurrent.futures.as_completed(tasks):
                    try:
                        result = future.result()
                        if result is not None:
                            rows.extend(result)
                    except Exception as exc:
                        print(f"An error occurred while processing player: {str(exc)}")
                        sys.exit(1)
                            
        combined_df = pd.DataFrame(rows)
        combined_df.to_csv(f'/tmp/{filename}-market.csv', index=False, mode='w+', header=True)
        print("Successfully extracted player market data.")

    except Exception as e:
        print(f"An error occurred while extracting player info: {str(e)}")
        sys.exit(1)

def parse_currency(currency_str: str) -> int:
    """
    Parse the currency string and convert it to an integer value.

    Args:
        currency_str: The currency string to be parsed.

    Returns:
        The parsed currency value as an integer.

    Raises:
        ValueError: If the currency string is not in the expected format.
    """
    try:
        if currency_str == "-":
            return None

        multiplier = 1
        try:
            if currency_str.endswith("m"):
                multiplier = 1000000
            elif currency_str.endswith("k"):
                multiplier = 1000
            return int(float(currency_str.replace("€", "").replace("m", "").replace("k", "")) * multiplier)
        except Exception:
            return None
    except ValueError:
        print("Invalid currency format")
        sys.exit(1)
    
if __name__ == "__main__":
    import time
    start_time = time.time()

    main()

    end_time = time.time()

    print(f"Execution time: {end_time - start_time} seconds")