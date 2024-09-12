import asyncio
from typing import Dict, List, Tuple
from bs4 import BeautifulSoup
import aiohttp
import aiofiles
from datetime import datetime, timedelta
import os
import re

async def fetch_image(session: aiohttp.ClientSession, url: str, output_dir: str, filename: str) -> str:
    """
    Fetch image from URL and save it locally in the 'live_scores/icons' directory.
    
    :param session: aiohttp ClientSession
    :param url: URL of the image
    :param output_dir: Directory to save the image
    :param filename: Filename to save the image as
    :return: Relative path to the saved image
    """
    try:
        # Define the icons directory
        icons_dir = os.path.join(output_dir, 'icons')
        
        # Ensure the 'icons' directory exists within the output directory
        os.makedirs(icons_dir, exist_ok=True)
        
        # Sanitize the filename to remove or replace invalid characters
        sanitized_filename = re.sub(r'[^\w\-_\. ]', '_', filename)
        
        # Extract the team name from the sanitized filename to create a subdirectory
        team_name = sanitized_filename.split('_')[0]
        team_dir = os.path.join(icons_dir, team_name)
        os.makedirs(team_dir, exist_ok=True)
        
        async with session.get(url) as response:
            if response.status == 200:
                content = await response.read()
                image_path = os.path.join(team_dir, sanitized_filename)
                async with aiofiles.open(image_path, 'wb') as f:
                    await f.write(content)
                
                # Return the relative path for use in Markdown
                relative_path = os.path.relpath(image_path, start=os.getcwd())
                return relative_path
    except Exception as e:
        print(f"Error fetching image {url}: {e}")
    return ""

async def process_match(match: BeautifulSoup, session: aiohttp.ClientSession, output_dir: str) -> Dict[str, str]:
    """
    Process a single match and extract relevant information.
    
    :param match: BeautifulSoup object representing a match
    :param session: aiohttp ClientSession
    :param output_dir: Directory to save images
    :return: Dictionary containing match information
    """
    home_team = match.select_one('.verein-heim a').text.strip().replace("'", "\\'").replace("'", "\\").replace("'", "\\")
    away_team = match.select_one('.verein-gast a').text.strip().replace("'", "\\'").replace("'", "\\").replace("'", "\\")
    
    score_element = match.select_one('.ergebnis a span')
    score = score_element.text.strip() if score_element else "N/A"
    
    home_icon_url = match.select_one('.verein-heim img')['data-src']
    away_icon_url = match.select_one('.verein-gast img')['data-src']
    
    home_icon_path = await fetch_image(session, home_icon_url, output_dir, f"{home_team}_icon.png")
    away_icon_path = await fetch_image(session, away_icon_url, output_dir, f"{away_team}_icon.png")
    
    round_info = match.select_one('.zeit').text.strip() if match.select_one('.zeit') else ""
    
    return {
        'home_team': home_team,
        'away_team': away_team,
        'score': score,
        'home_icon': home_icon_path,
        'away_icon': away_icon_path,
        'round': round_info
    }

async def process_competition(competition: BeautifulSoup, session: aiohttp.ClientSession, output_dir: str) -> Tuple[str, str, List[Dict[str, str]]]:
    """
    Process a competition and its matches.
    
    :param competition: BeautifulSoup object representing a competition
    :param session: aiohttp ClientSession
    :param output_dir: Directory to save images
    :return: Tuple containing competition name, icon, and list of matches
    """
    comp_name = competition.select_one('h2 a').text.strip()
    comp_icon_url = competition.select_one('h2 img')['data-src']
    
    comp_icon_path = await fetch_image(session, comp_icon_url, output_dir, f"{comp_name}_icon.png")
    
    matches = []
    for match in competition.find_next('table', class_='livescore').select('tr.begegnungZeile'):
        matches.append(await process_match(match, session, output_dir))
    
    return comp_name, comp_icon_path, matches

async def scrape_and_create_markdown(html_content: str, output_dir: str) -> str:
    """
    Scrape HTML content and create a structured markdown string.
    
    :param html_content: HTML content to scrape
    :param output_dir: Directory to save images
    :return: Structured markdown string
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    competitions = soup.select('.kategorie')
    
    # Get today's date and yesterday's date
    today = datetime.now()
    yesterday = today - timedelta(1)
    today_str = today.strftime('%Y-%m-%d')
    yesterday_str = yesterday.strftime('%Y-%m-%d')

    # Add the date and a link to yesterday's scores at the top of the markdown

    markdown = f"# Live Scores - {today_str}\n\n"
    markdown += f"[See yesterday's scores ({yesterday_str})](https://github.com/salimt/Transfermarkt-ETL-and-LIVE-Scores/tree/main/live_scores/live_scores_{yesterday.strftime('%Y%m%d')}.md)\n\n"

    
    # markdown = f"# Live Scores - {today_str}\n\n"
    # markdown += f"[See yesterday's scores ({yesterday_str})]({output_dir}/live_scores_{yesterday.strftime('%Y%m%d')}.md)\n\n"
        
    async with aiohttp.ClientSession() as session:
        for competition in competitions:
            comp_name, comp_icon, matches = await process_competition(competition, session, output_dir)
            comp_name  = comp_name.replace("'","")
            # Adjust the path to be a raw GitHub link
            comp_icon = comp_icon.replace(os.getcwd(), '').lstrip('/')
            comp_icon_url = f"https://github.com/salimt/Transfermarkt-ETL-and-LIVE-Scores/raw/main/{comp_icon}"
            
            markdown += f"## <img src='{comp_icon_url}' alt='{comp_name}' style='width:5%; height:5%; display:inline-block; vertical-align:middle;' /> {comp_name}\n\n"
            
            # Center the table with a div, keeping the table in Markdown format
            markdown += "<div align='center'>\n\n"
            
            # Add the table in Markdown format
            markdown += "| Round | Home Team | Score | Away Team |\n"
            markdown += "|:------|:----------|:-----:|:----------|\n"
            
            for match in matches:
                # Adjust the paths to be raw GitHub links
                home_icon = match['home_icon'].replace(os.getcwd(), '').lstrip('/')
                away_icon = match['away_icon'].replace(os.getcwd(), '').lstrip('/')
                match['home_team'] = match['home_team'].replace("'","")
                match['away_team'] = match['away_team'].replace("'","")
                
                home_icon_url = f"https://github.com/salimt/Transfermarkt-ETL-and-LIVE-Scores/raw/main/{home_icon}"
                away_icon_url = f"https://github.com/salimt/Transfermarkt-ETL-and-LIVE-Scores/raw/main/{away_icon}"
                
                markdown += (f"| {match['round']} | "
                             f"<img src='{home_icon_url}' alt='{match['home_team']}' width='30%' height='30%' /> {match['home_team']} | "
                             f"**{match['score']}** | "
                             f"{match['away_team']} <img src='{away_icon_url}' alt='{match['away_team']}' width='25%' height='25%' /> |\n")
            
            # Close the div tag
            markdown += "\n</div>\n\n"
    
    return markdown


async def fetch_html(url: str) -> str:
    """
    Fetch HTML content from a URL.
    
    :param url: URL to fetch HTML content from
    :return: HTML content as a string
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.text()

async def main(url: str, output_dir: str) -> None:
    html_content = await fetch_html(url)
    markdown_content = await scrape_and_create_markdown(html_content, output_dir)
    
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate filename with current date in YYYYMMDD format
    date_str = datetime.now().strftime('%Y%m%d')
    output_file = f"{output_dir}/live_scores_{date_str}.md"
    
    # Save the markdown file
    async with aiofiles.open(output_file, 'w', encoding='utf-8') as f:
        await f.write(markdown_content)
    
    # Update README.md
    async with aiofiles.open('README.md', 'w', encoding='utf-8') as f:
        await f.write(markdown_content)
    
if __name__ == "__main__":
    # Get today's date
    today = datetime.now()
    today_str = today.strftime('%Y-%m-%d')

    # Update the URL with today's date
    url = f'https://www.transfermarkt.com/live/index?datum={today_str}'
    output_dir = os.path.join(os.getcwd(), 'live_scores')
    asyncio.run(main(url, output_dir))
