from email.utils import parsedate_to_datetime
from datetime import datetime, timedelta, timezone
import sys

import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import json
import os
import argparse
from dotenv import load_dotenv

def fetch_google_news(query, hl="ko", gl="KR"):
    # ... existing code ...
    encoded_query = urllib.parse.quote(query + " when:1d") # Try adding Google search operator for 1 day
    # Note: RSS parameters might not support 'when:1d' perfectly, so we still need manual filtering.
    url = f"https://news.google.com/rss/search?q={encoded_query}&hl={hl}&gl={gl}&ceid={gl}:{hl}"
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            return response.read()
    except urllib.error.URLError as e:
        print(f"Error fetching news for {query}: {e}")
        return None

def parse_news(xml_content):
    if not xml_content:
        return []
    
    try:
        root = ET.fromstring(xml_content)
        items = []
        
        # Filter for last 24 hours
        now = datetime.now(timezone.utc)
        one_day_ago = now - timedelta(days=1)
        
        for item in root.findall('./channel/item'):
            title = item.find('title').text if item.find('title') is not None else "No Title"
            link = item.find('link').text if item.find('link') is not None else ""
            pub_date_str = item.find('pubDate').text if item.find('pubDate') is not None else ""
            description = item.find('description').text if item.find('description') is not None else ""
            
            # Date Filtering
            if pub_date_str:
                try:
                    pub_date = parsedate_to_datetime(pub_date_str)
                    if pub_date < one_day_ago:
                        continue # Skip old news
                except Exception as e:
                    print(f"Error parsing date '{pub_date_str}': {e}")
                    # If date parsing fails, maybe include it or skip? Let's skip to be safe.
                    continue
            else:
                continue

            items.append({
                'title': title,
                'link': link,
                'pubDate': pub_date_str,
                'description': description
            })
        return items
    except ET.ParseError as e:
        print(f"Error parsing XML: {e}")
        return []

def main():
    load_dotenv()
    
    parser = argparse.ArgumentParser(description="Fetch news from Google News")
    parser.add_argument("--alias", type=str, help="Blog Alias for looking up default topic in .env")
    parser.add_argument("--hl", type=str, default="ko", help="Host Language (e.g. ko, en)")
    parser.add_argument("--gl", type=str, default="KR", help="Geolocation (e.g. KR, US)")
    parser.add_argument("queries", nargs="*", help="List of topics to search")
    args = parser.parse_args()

    queries = args.queries

    if not queries and args.alias:
        target_alias = args.alias.upper()
        for i in range(1, 6):
            env_alias = os.getenv(f"TISTORY_ALIAS_{i}")
            if env_alias and env_alias.upper() == target_alias:
                default_topic = os.getenv(f"TISTORY_DEFAULT_TOPIC_{i}")
                if default_topic:
                    queries = [q.strip() for q in default_topic.split(",") if q.strip()]
                break
            
    if not queries:
        queries = ["경제", "부동산"]
    
    print(f"Fetching news for keywords (last 24h): {queries}")
    all_news = []
    
    # Check if we should use the default "half Korean, half US" behavior
    use_default_mixed_regions = (args.hl == "ko" and args.gl == "KR")
    
    for query in queries:
        if use_default_mixed_regions:
            # Fetch Korean New
            print(f"Fetching KR news for: {query}")
            kr_xml = fetch_google_news(query, hl="ko", gl="KR")
            all_news.extend(parse_news(kr_xml))
            
            # Fetch US News
            print(f"Fetching US news for: {query}")
            us_xml = fetch_google_news(query, hl="en", gl="US")
            all_news.extend(parse_news(us_xml))
        else:
            print(f"Fetching news for: {query} (hl={args.hl}, gl={args.gl})")
            xml_content = fetch_google_news(query, hl=args.hl, gl=args.gl)
            all_news.extend(parse_news(xml_content))
        
    # Deduplicate based on link or title
    unique_news = {item['title']: item for item in all_news}.values() 
    
    output_dir = ".tmp"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    output_file = os.path.join(output_dir, "news_data.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(list(unique_news), f, ensure_ascii=False, indent=2)
        
    print(f"Saved {len(unique_news)} relevant news items (last 24h) to {output_file}")

if __name__ == "__main__":
    main()
