import subprocess
try:
    import pandas
except ImportError:
    subprocess.check_call(["pip", "install", "pandas"])

try:
    import bs4
except ImportError:
    subprocess.check_call(["pip", "install", "beautifulsoup4"])

from bs4 import BeautifulSoup
import datetime
import sys
import pandas as pd
from typing import List, Optional
import validation as va
from concurrent.futures import ThreadPoolExecutor
import aiohttp
from aiohttp import ClientSession, http_exceptions
import asyncio
import re


class PlayerInfoScraper:
    def __init__(self, url: str):
        self.url = url
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36"
        }

    async def scrape_player_data(self, player_urls: List[str]) -> List[dict]:
        """
        Scrapes player data from the given player URLs.

        Args:
            player_urls (List[str]): List of player URLs to scrape.
        """
        # print(f"Scraping data for {len(player_urls)} players...")  # Debug print

        async with aiohttp.ClientSession() as session:
            tasks = []
            for url in player_urls:
                tasks.append(self.scrape_single_player(session, url))

            player_data = await asyncio.gather(*tasks)
            await asyncio.sleep(0)

        # print("Player data have been scraped successfully.")
        return player_data

    async def scrape_single_player(self, session, url: str) -> dict:
        #print(f"Scraping data for player at {url}...")  # Debug print

        player_data = {}
        for _ in range(3):  # Retry up to 3 times
            try:
                async with session.get(url, headers=self.headers) as response:
                    soup = BeautifulSoup(await response.text(errors='ignore'), 'lxml')
                    await asyncio.sleep(0)

                    # Extracting the player ID
                    player_id = url.split("/")[-1]

                    shirt_number_elem = soup.find("span", class_="data-header__shirt-number")
                    if shirt_number_elem:
                        shirt_number_text = shirt_number_elem.text.strip().replace("#", "")
                        shirt_number = None if shirt_number_text == 'N/A' else shirt_number_text
                    else:
                        shirt_number = None

                    full_name_elem = soup.find("h1", class_="data-header__headline-wrapper")
                    if full_name_elem:
                        full_name_text = full_name_elem.text.strip()
                        full_name = None if full_name_text == 'N/A' else full_name_text.split(maxsplit=1)[1] if len(full_name_text.split(maxsplit=1)) > 1 else None
                    else:
                        full_name = None

                    # Extracting date of birth
                    date_of_birth_elem = soup.find("span", itemprop="birthDate")
                    try:
                        date_of_birth = datetime.datetime.strptime(date_of_birth_elem.text.strip().split(' (')[0], "%b %d, %Y").strftime("%Y-%m-%d") if date_of_birth_elem and date_of_birth_elem.text.strip().split(' (')[0] != 'N/A' else None
                    except ValueError:
                        date_of_birth = None

                    height_elem = soup.find('span', itemprop='height')
                    if height_elem:
                        height_text = height_elem.text
                        height = re.sub(r'\D', '', height_text)
                    else:
                        height = None

                    # Initialize an empty dictionary to store player data
                    player_personal = {}

                    # Initialize date_of_death with a default value
                    player_personal['Date of death'] = None

                    # Find the list item with the class "data-header__label" and Iterate through each list item
                    for li in soup.find_all('li', class_='data-header__label'):
                        if 'Date of death' in li.text:
                            date_text = li.text.split(':')[-1].strip()
                            date_text = re.sub(r'\([^)]*\)', '', date_text)  # Remove anything within parentheses
                            date_text = date_text.strip()  # Remove any leading/trailing whitespace
                            try:
                                date_of_death = datetime.datetime.strptime(date_text, '%d.%m.%Y').strftime('%Y-%m-%d')
                            except ValueError:
                                date_of_death = None
                            player_personal['Date of death'] = date_of_death
                        if 'Date of birth/Age' in li.text:
                            continue
                        if 'Height' in li.text:
                            continue
                        if 'Caps/Goals' in li.text:
                            # Extract the 'Caps/Goals' value
                            caps_goals_str = li.text.split('Caps/Goals:')[-1].strip()

                            # Split the string by '/' to separate Caps and Goals
                            caps, goals = caps_goals_str.split('/')
                            caps = caps.strip()
                            goals = goals.strip()
                            player_personal['Caps'] = caps
                            player_personal['Goals'] = goals
                            continue

                        # Split the text of the list item by ":" to separate column name and value
                        parts = li.text.strip().split(":")
                        # Extract the column name (remove leading/trailing whitespaces)
                        column_name = parts[0].strip()
                        # Extract the value (remove leading/trailing whitespaces)
                        value = parts[1].strip()
                        # Map the column name to the appropriate key in the dictionary
                        player_personal[column_name] = value

                    # Extracting club and league
                    club_elem = soup.find('span', {'class': 'data-header__club'})
                    try:
                        club = club_elem.find('a').get_text(strip=True) if club_elem else None
                    except AttributeError:
                        club = None

                    league_elem = soup.find('a', {'class': 'data-header__league-link'})
                    try:
                        league = league_elem.get_text(strip=True) if league_elem else None
                    except AttributeError:
                        league = None

                    # Extracting joined date
                    joined_elem = soup.find('span', {'class': 'data-header__label'})
                    if joined_elem and joined_elem.find_next_sibling('span'):
                        joined_text = joined_elem.find_next_sibling('span').get_text(strip=True).replace("Joined:", "")
                        try:
                            joined = datetime.datetime.strptime(joined_text, "%b %d, %Y").strftime("%Y-%m-%d") if joined_text and joined_text != "-" and joined_text != 'N/A' else None
                        except ValueError:
                            joined = None
                    else:
                        joined = None

                    # Extracting contract expiration date
                    if joined_elem and joined_elem.find_next_sibling('span') and joined_elem.find_next_sibling('span').find_next_sibling('span'):
                        contract_expires_text = joined_elem.find_next_sibling('span').find_next_sibling('span').get_text(strip=True).replace("Contract expires:", "")
                        try:
                            contract_expires = datetime.datetime.strptime(contract_expires_text, "%b %d, %Y").strftime("%Y-%m-%d") if contract_expires_text and contract_expires_text != "-" and contract_expires_text != 'N/A' else None
                        except ValueError:
                            contract_expires = None
                    else:
                        contract_expires = None

                    player_img_elem = soup.find('meta', property='og:image')
                    player_img = player_img_elem['content'] if player_img_elem else None

                    player_data = {
                        "player_id": player_id,
                        "shirt_number": shirt_number,
                        "full_name": full_name,
                        **player_personal,
                        "date_of_birth": date_of_birth,
                        "height": height,
                        "club": club,
                        "league": league,
                        "joined": joined,
                        "contract_expires": contract_expires,
                        "player_img": player_img,
                        "url": url
                    }
                return player_data
            except http_exceptions.TransferEncodingError:
                print(f"TransferEncodingError occurred while accessing {url}. Retrying...")
            except Exception as e:
                print(f"An error occurred while scraping player data: {e}")
                sys.exit(1)
        print(f"Failed to scrape data for player at {url} after 3 attempts.")
        return None  # Return None or an appropriate value if the error persists
    
        # return player_data

    async def get_club_links(self) -> List[str]:
        """
        Retrieves the links to the clubs from the main URL.

        Returns:
            List[str]: List of club links.
        """
        # print("Getting club links...")  # Debug print

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.url, headers=self.headers) as response:
                    text = await response.text()
                    await asyncio.sleep(0)
                    soup = BeautifulSoup(text, 'html.parser')

                    # Find all <a> tags within <td> tags
                    links = soup.find_all('td', class_='hauptlink no-border-links')

                    club_links = []
                    # Extract href attributes
                    for link in links:
                        href = link.a['href']
                        club_links.append("https://www.transfermarkt.com" + href)

                    # print(f"Got {len(club_links)} club links.")  # Debug print
                    return club_links
        except Exception as e:
            print(f"An error occurred while getting club links: {e}")
            if '443' in str(e):
                print("Error 443 occurred. Sleeping and retrying...")
                time.sleep(20)  # Sleep for 10 seconds
            else:
                raise e
            
            # sys.exit(1)

    async def get_player_links(self, urls: List[str]) -> List[str]:
        """
        Retrieves the links to the players from the given club URLs.

        Args:
            urls (List[str]): List of club URLs.

        Returns:
            List[str]: List of player links.
        """
        # print(f"Getting player links from {len(urls)} URLs...")  # Debug print

        tasks = [self.get_links_from_single_page(url) for url in urls]
        player_links = await asyncio.gather(*tasks)
        await asyncio.sleep(0)

        # Flatten the list of lists
        player_links = [link for sublist in player_links for link in sublist]

        # print(f"Got {len(player_links)} player links.")  # Debug print
        return player_links

    async def get_links_from_single_page(self, url: str) -> List[str]:
        """
        Retrieves the links to the players from the given URL.

        Args:
            url (str): The URL of the page.

        Returns:
            List[str]: List of player links.
        """
        hrefs = []
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers) as response:
                    text = await response.text(errors='ignore')
                    await asyncio.sleep(0)
                    soup = BeautifulSoup(text, 'html.parser')
                    # Find all <a> tags within <td> tags with class="hauptlink"
                    links = soup.find_all('td', class_='hauptlink')

                    # Extract href attribute from each <a> tag
                    hrefs.extend(["https://www.transfermarkt.com" + link.find('a').get('href') for link in links if link.find('a') and 'profil/spieler' in link.find('a').get('href')])
        except Exception as e:
            print(f"An error occurred while getting player links: {e}")
            if '443' in str(e):
                print("Error 443 occurred. Sleeping and retrying...")
                time.sleep(20)  # Sleep for 10 seconds
            else:
                raise e
            # sys.exit(1)

        return hrefs


async def main(urls) -> None:
    """
    The main function of the script. It constructs a URL for a specific league and season, 
    validates the output name, checks if the output file already exists, and if not, 
    it initiates a scraping process to gather player data from the constructed URL and saves it to a file.

    :param vars: A list of strings that represent the league name, league code, and season respectively.
    :param url: A string that represents the URL to scrape data from, constructed using the vars list.
    :param output_name: The name of the output, passed as a command line argument.
    :param scraper: An instance of the PlayerInfoScraper class.
    :param club_links: A list of URLs for each club in the league.
    :param player_links: A list of URLs for each player in the league.
    """
    output_name = sys.argv[1]
    try:
        import os
        va.validate_input(output_name)
        output_file = f'/tmp/{output_name}-profiles.csv'
        processed_urls_file = f'/tmp/{output_name}-profiles-processed-urls.txt'

        # Load processed URLs
        if os.path.exists(processed_urls_file):
            with open(processed_urls_file, 'r') as f:
                processed_urls = f.read().splitlines()
        else:
            processed_urls = []

        # Load existing data
        if os.path.exists(output_file):
            all_player_data = pd.read_csv(output_file).to_dict('records')
        else:
            all_player_data = []


        for url in urls:
            if url in processed_urls:
                print(f"URL {url} has already been processed. Skipping.")
                continue

            scraper = PlayerInfoScraper(url)
            club_links = await scraper.get_club_links()
            await asyncio.sleep(0)
            player_links = await scraper.get_player_links(club_links)
            await asyncio.sleep(0)
            player_data = await scraper.scrape_player_data(player_links)
            await asyncio.sleep(0)
            all_player_data.extend(player_data)
            print(f"Scraped {len(player_data)} players from {url}.")

            # Save progress after each URL
            df = pd.DataFrame(all_player_data)
            df.to_csv(output_file, index=False, mode='w+', header=True)

            # Add URL to processed URLs list
            with open(processed_urls_file, 'a') as f:
                f.write(url + '\n')

    except Exception as e:
        print(f"An error occurred: {e}")
        if '443' in str(e):
            print("Error 443 occurred. Sleeping and retrying...")
            time.sleep(20)  # Sleep for 10 seconds
        else:
            raise e
        # sys.exit(1)

if __name__ == "__main__":
    import time
    import get_league_links as leagues
    urls = leagues.get_league_links()
    start_time = time.time()

    asyncio.run(main(urls))

    end_time = time.time()

    print(f"Execution time: {end_time - start_time} seconds")