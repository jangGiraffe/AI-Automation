import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import json
import os
import sys
from datetime import datetime, timedelta

def fetch_google_news(query):
    encoded_query = urllib.parse.quote(query)
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
        
        # Namespace handling might be needed depending on the RSS feed, 
        # but Google News RSS is usually standard.
        for item in root.findall('./channel/item'):
            title = item.find('title').text if item.find('title') is not None else "No Title"
            link = item.find('link').text if item.find('link') is not None else ""
            pub_date_str = item.find('pubDate').text if item.find('pubDate') is not None else ""
            description = item.find('description').text if item.find('description') is not None else ""
            
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
    # Use command line arguments if provided, otherwise default
    if len(sys.argv) > 1:
        queries = sys.argv[1:]
    else:
        queries = ["경제", "부동산"]
    
    print(f"Fetching news for keywords: {queries}")
    all_news = []
    
    for query in queries:
        print(f"Fetching news for: {query}")
        xml_content = fetch_google_news(query)
        news_items = parse_news(xml_content)
        all_news.extend(news_items)
        
    # Deduplicate based on link
    unique_news = {item['title']: item for item in all_news}.values() # Dedupe by title to be safe
    
    output_dir = ".tmp"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    output_file = os.path.join(output_dir, "news_data.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(list(unique_news), f, ensure_ascii=False, indent=2)
        
    print(f"Saved {len(unique_news)} news items to {output_file}")

if __name__ == "__main__":
    main()
