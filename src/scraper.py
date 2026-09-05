import asyncio
import aiohttp
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime, timezone

async def fetch_page(session, url):
    """Fetches the HTML content of a URL asynchronously."""
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    try:
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                return await response.text()
            else:
                print(f"Failed to fetch {url}: Status {response.status}")
                return None
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

async def get_github_stars(session, github_url):
    """Extracts repo name from URL and calls GitHub API for live stars."""
    # This regex looks for the "username/repository" part of the URL
    match = re.search(r'github\.com/([^/]+)/([^/]+)', github_url)
    if not match:
        return 0
    
    user, repo = match.group(1), match.group(2)
    api_url = f"https://api.github.com/repos/{user}/{repo}"
    
    headers = {'Accept': 'application/vnd.github.v3+json'}
    try:
        async with session.get(api_url, headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                return data.get('stargazers_count', 0)
    except Exception as e:
        print(f"GitHub API error: {e}")
    return 0

async def main():
    # We will simulate scraping a paper that has a known GitHub repo
    # In a real run, your script will extract these links dynamically from the HTML
    simulated_paper_title = "Attention Is All You Need"
    simulated_authors = ["Ashish Vaswani", "Noam Shazeer", "Niki Parmar"]
    paper_url = "https://arxiv.org/abs/1706.03762"
    github_url = "https://github.com/tensorflow/tensor2tensor" 

    async with aiohttp.ClientSession() as session:
        print("Fetching live GitHub stars...")
        stars = await get_github_stars(session, github_url)
        
        # Build the exact schema requested by the assignment
        research_paper_entity = {
            "schemaVersion": "1.0",
            "recordType": "RESEARCH_PAPER",
            "content": {
                "title": simulated_paper_title,
                "authors": simulated_authors,
                "paper_url": paper_url,
                "github_url": github_url,
                "github_stars": stars,
                "published_date": datetime.now(timezone.utc).isoformat() # Mocking date for now
            }
        }
        
        print("\n--- Extracted Entity ---")
        # Print the dictionary as formatted JSON
        print(json.dumps(research_paper_entity, indent=4))

if __name__ == "__main__":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())