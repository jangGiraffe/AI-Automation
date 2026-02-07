import os
import sys
import requests
import json
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

API_KEY = os.getenv("GOOGLE_API_KEY")
if not API_KEY:
    raise ValueError("GOOGLE_API_KEY not found in .env file")

def generate_hashtags(html_path):
    if not os.path.exists(html_path):
        print(f"HTML file not found: {html_path}")
        return

    with open(html_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')

    # Extract text content for context (first 2000 chars is usually enough)
    text_content = soup.get_text(separator=' ', strip=True)[:2000]

    # Gemini API URL (Gemini 2.0 Flash)
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY}"
    
    headers = {
        "Content-Type": "application/json"
    }
    
    prompt_text = f"Analyze the following blog post content and generate 10 relevant, trending Korean hashtags. Format the output as a single line of space-separated hashtags (e.g., #Keyword1 #Keyword2). Do not include any other text or explanations.\n\nContent:\n{text_content}"

    payload = {
        "contents": [{
            "parts": [{"text": prompt_text}]
        }]
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            try:
                hashtags = result['candidates'][0]['content']['parts'][0]['text'].strip()
                print(f"Generated Hashtags: {hashtags}")

                # Append to HTML
                hashtag_div = soup.new_tag("div", attrs={"class": "hashtag-section", "style": "margin-top: 30px; font-size: 0.9em; color: #718096; text-align: center;"})
                hashtag_div.string = hashtags
                
                # Insert before footer or at the end of container
                footer = soup.find("div", class_="footer")
                if footer:
                    footer.insert_before(hashtag_div)
                else:
                    container = soup.find("div", class_="container")
                    if container:
                        container.append(hashtag_div)
                    else:
                        soup.body.append(hashtag_div)

                with open(html_path, 'w', encoding='utf-8') as f:
                    f.write(str(soup))
                print(f"Hashtags appended to: {html_path}")
                
            except (KeyError, IndexError) as e:
                print(f"Error parsing API response: {e}")
                print(f"Response: {result}")
        else:
            print(f"Error: {response.status_code}, {response.text}")

    except Exception as e:
        print(f"Error generating hashtags: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: py execution/generate_hashtags.py <html_path>")
        sys.exit(1)
    
    html_path = sys.argv[1]
    generate_hashtags(html_path)
