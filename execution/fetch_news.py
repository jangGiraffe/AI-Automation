from email.utils import parsedate_to_datetime
from datetime import datetime, timedelta, timezone
import sys

import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import json
import os

def fetch_google_news(query):
    # ... existing code ...
    encoded_query = urllib.parse.quote(query + " when:1d") # Try adding Google search operator for 1 day
    # Note: RSS parameters might not support 'when:1d' perfectly, so we still need manual filtering.
    url = f"https://news.google.com/rss/search?q={encoded_query}&hl=ko&gl=KR&ceid=KR:ko"
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
    # ... existing code ...
    if len(sys.argv) > 1:
        queries = sys.argv[1:]
    else:
        queries = ["경제", "부동산"]
    
    print(f"Fetching news for keywords (last 24h): {queries}")
    all_news = []
    
    for query in queries:
        print(f"Fetching news for: {query}")
        xml_content = fetch_google_news(query)
        news_items = parse_news(xml_content)
        all_news.extend(news_items)
        
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
