import os
import time
import requests
import re
import sys
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

API_KEY = os.getenv("GOOGLE_API_KEY")
if not API_KEY:
    raise ValueError("GOOGLE_API_KEY not found in .env file")

def generate_image_with_gemini(prompt, output_path):
    """
    Generates an image using Google Gemini (Imagen 3/4) API via REST.
    """
    # Using 'imagen-4.0-generate-001' as it was found in the model list
    url = f"https://generativelanguage.googleapis.com/v1beta/models/imagen-4.0-generate-001:predict?key={API_KEY}"
    
    headers = {
        "Content-Type": "application/json"
    }
    
    payload = {
        "instances": [
            {
                "prompt": prompt
            }
        ],
        "parameters": {
            "sampleCount": 1,
            "aspectRatio": "16:9" 
        }
    }

    try:
        print(f"Generating image for prompt: '{prompt}'...")
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            # The response structure for Imagen 3 via AI Studio API might vary slightly, 
            # typically it returns base64 encoded image in predictions.
            # adjusting for common response format:
            # { "predictions": [ { "bytesBase64Encoded": "..." } ] }
            
            predictions = result.get('predictions')
            if predictions and len(predictions) > 0:
                image_data_b64 = predictions[0].get('bytesBase64Encoded')
                if image_data_b64:
                    import base64
                    image_data = base64.b64decode(image_data_b64)
                    
                    # Ensure directory exists
                    os.makedirs(os.path.dirname(output_path), exist_ok=True)
                    
                    with open(output_path, "wb") as f:
                        f.write(image_data)
                    print(f"Successfully saved image to: {output_path}")
                    return True
            print(f"Failed to extract image from response: {result}")
            return False
            
        elif response.status_code == 429:
            print("Quota exceeded (429). Waiting for 60 seconds before retrying...")
            time.sleep(60)
            return generate_image_with_gemini(prompt, output_path) # Recursive retry
            
        else:
            print(f"Error: {response.status_code}, {response.text}")
            return False
            
    except Exception as e:
        print(f"Exception during image generation: {e}")
        return False

def process_html_for_images(html_path):
    if not os.path.exists(html_path):
        print(f"HTML file not found: {html_path}")
        return

    with open(html_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')

    img_tags = soup.find_all('img')
    base_dir = os.path.dirname(html_path)
    
    html_modified = False

    for i, img in enumerate(img_tags):
        src = img.get('src')
        alt = img.get('alt', '')
        prompt = img.get('data-prompt', alt) 
        
        if not src:
            continue
        
        # Determine target local filename
        # If it's already a local file, use it. If it's external/placeholder, create a new name.
        if src.startswith("http") or src.startswith("https"):
            # It's an external URL (placeholder), so we want to save it locally
            filename = f"image_{i+1}.png" # e.g., image_1.png
            img['src'] = filename
            html_modified = True
            print(f"Mapped external src '{src}' to local file '{filename}'")
        elif "images/" in src or "images\\" in src:
             # Fix old 'images/' path
             filename = os.path.basename(src)
             img['src'] = filename
             html_modified = True
        else:
             filename = os.path.basename(src)

        # Construct full local path (flat structure: same as HTML)
        image_path = os.path.normpath(os.path.join(base_dir, filename))
        
        if os.path.exists(image_path):
            print(f"Image already exists: {image_path}")
        else:
            # Check if it exists in the old 'images/' subdirectory and move it if so
            old_image_path = os.path.join(base_dir, 'images', filename)
            if os.path.exists(old_image_path):
                print(f"Moving existing image from {old_image_path} to {image_path}")
                os.rename(old_image_path, image_path)
                # Remove empty images dir if possible
                try:
                    os.rmdir(os.path.dirname(old_image_path))
                except:
                    pass
            else:
                print(f"Missing image: {image_path}")
                print(f"Prompt: {prompt}")
                
                # Simple retry loop
                max_retries = 3
                for attempt in range(max_retries):
                    success = generate_image_with_gemini(prompt, image_path)
                    if success:
                        break
                    else:
                        print(f"Retry {attempt + 1}/{max_retries} failed.")
                        time.sleep(5)

    if html_modified:
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(str(soup))
        print(f"Updated HTML file with flat image paths: {html_path}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Retry missing images for a blog post.")
    parser.add_argument("html_path", help="Path to the blog post HTML file")
    
    args = parser.parse_args()
    process_html_for_images(args.html_path)
