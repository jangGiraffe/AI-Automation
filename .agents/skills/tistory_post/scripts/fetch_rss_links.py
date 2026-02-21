import feedparser
import json
import os
import sys
from dotenv import load_dotenv

def fetch_rss_links(blog_name):
    """
    Fetch posts from Tistory RSS and return a list of {title, link}
    """
    rss_url = f"https://{blog_name}.tistory.com/rss"
    print(f"Fetching RSS from: {rss_url}")
    
    feed = feedparser.parse(rss_url)
    
    posts = []
    if feed.entries:
        for entry in feed.entries:
            posts.append({
                "title": entry.title,
                "link": entry.link
            })
    
    return posts

def main():
    load_dotenv()
    
    # Example: python fetch_internal_links.py <blog_name>
    if len(sys.argv) < 2:
        print("Usage: python fetch_internal_links.py <blog_name>")
        sys.exit(1)
        
    blog_name = sys.argv[1]
    
    try:
        posts = fetch_rss_links(blog_name)
        
        output_path = ".tmp/internal_links.json"
        os.makedirs(".tmp", exist_ok=True)
        
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(posts, f, ensure_ascii=False, indent=2)
            
        print(f"Successfully saved {len(posts)} posts to {output_path}")
        
    except Exception as e:
        print(f"Error fetching RSS: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
