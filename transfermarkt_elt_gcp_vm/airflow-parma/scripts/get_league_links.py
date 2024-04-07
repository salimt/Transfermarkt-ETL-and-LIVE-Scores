import subprocess
try:
    import pandas
except ImportError:
    subprocess.check_call(["pip", "install", "pandas"])


try:
    import bs4
except ImportError:
    subprocess.check_call(["pip", "install", "beautifulsoup4"])

import aiohttp
from aiohttp import ClientSession, http_exceptions
import asyncio
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from typing import List

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
}

async def fetch(session, url, retries=3):
    for i in range(retries):
        try:
            async with session.get(url) as response:
                return await response.text()
        except http_exceptions.TransferEncodingError:
            print(f"TransferEncodingError occurred while accessing {url}. Attempt {i+1} of {retries}")
            if i == retries - 1:  # This was the last attempt
                raise  # Re-raise the last exception

async def collect_league_links(url: str) -> List[str]:
    all_league_links = set()
    async with aiohttp.ClientSession(headers=headers) as session:
        while url:
            response = await fetch(session, url)
            soup = BeautifulSoup(response, 'html.parser')
            league_elements = soup.find_all('a', href=True)
            for link in league_elements:
                href = link.get('href')
                if href and "/startseite/wettbewerb/" in href:
                    all_league_links.add(urljoin(url, href))
            next_page_element = soup.find("li", class_="tm-pagination__list-item--icon-next-page")
            if next_page_element:
                url = urljoin(url, next_page_element.find("a").get("href"))
            else:
                url = None
    return list(all_league_links)

def get_league_links():
    async def main() -> List[str]:
        url = "https://www.transfermarkt.com/wettbewerbe/europa"
        all_league_links = await collect_league_links(url)
        return all_league_links

    # To get the result, you can do:
    urls = asyncio.run(main())
    return urls
