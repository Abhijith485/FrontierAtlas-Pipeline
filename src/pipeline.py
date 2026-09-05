import asyncio
import aiohttp
import pandas as pd
import json
import time
import random
from scraper import fetch_page
from llm_engine import extract_startup_data

# A small mock list of URLs to process. 
# For the real task, you would load hundreds of URLs from a directory here.
TARGET_URLS = [
    "https://huggingface.co/anthropic",
    "https://huggingface.co/google",
    "https://huggingface.co/meta"
]

async def process_single_url(session, url, retries=3):
    """Fetches a URL and extracts data using the LLM with exponential backoff."""
    print(f"Processing: {url}")
    
    # 1. Scrape the HTML
    html_content = await fetch_page(session, url)
    if not html_content:
        return None

    # 2. Extract with LLM (including Rate Limit / 429 Handling)
    for attempt in range(retries):
        try:
            # We truncate the HTML to the first 5000 characters to avoid 413 Payload Too Large errors
            truncated_html = html_content[:5000] 
            result = extract_startup_data(truncated_html)
            
            if result:
                # Add the source URL back into the JSON before returning
                result['source'] = {'name': 'HuggingFace', 'url': url}
                return result
                
        except Exception as e:
            if "429" in str(e) or "quota" in str(e).lower():
                sleep_time = (2 ** attempt) + random.uniform(0, 1)
                print(f"Rate limited on {url}. Retrying in {sleep_time:.2f} seconds...")
                time.sleep(sleep_time)
            else:
                print(f"Error processing {url}: {e}")
                break
    return None

async def main():
    print("Initializing Data Ingestion Pipeline...")
    results = []
    
    async with aiohttp.ClientSession() as session:
        # Create concurrent tasks for all URLs
        tasks = [process_single_url(session, url) for url in TARGET_URLS]
        
        # Run them all at the same time
        extracted_data = await asyncio.gather(*tasks)
        
        # Filter out any failed extractions
        results = [data for data in extracted_data if data is not None]

    # 3. Flatten the JSON and export to CSV
    if results:
        print("\nPipeline Complete. Formatting data for Google Sheets...")
        
        # Flattening the nested JSON schema into rows and columns
        flat_data = []
        for item in results:
            flat_data.append({
                "schemaVersion": item.get("schemaVersion"),
                "recordType": item.get("recordType"),
                "source.name": item.get("source", {}).get("name"),
                "source.url": item.get("source", {}).get("url"),
                "content.entityName": item.get("content", {}).get("entityName"),
                "content.data.employeeCount": item.get("content", {}).get("data", {}).get("employeeCount")
            })
            
        df = pd.DataFrame(flat_data)
        df.to_csv("startups_output.csv", index=False)
        print("Success! Data saved to 'startups_output.csv'. You can now upload this to Google Sheets.")
    else:
        print("Pipeline failed to extract any valid data.")

if __name__ == "__main__":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())