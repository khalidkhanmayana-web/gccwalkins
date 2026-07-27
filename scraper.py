import json
import os
import requests
from bs4 import BeautifulSoup

TARGET_URL = "https://gccwalkin.com/"
DATA_FILE = "posts.json"

def fetch_job_image(job_url):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    try:
        res = requests.get(job_url, headers=headers, timeout=10)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            
            # Look for standard post containers where recruitment flyers live
            content_div = soup.find('div', class_='entry-content') or soup.find('div', class_='bs-content') or soup.find('article')
            
            if content_div:
                # Find all images inside the content
                images = content_div.find_all('img')
                for img in images:
                    # Check standard src or lazy-loading attributes
                    img_url = img.get('src') or img.get('data-src') or img.get('data-lazy-src')
                    if img_url:
                        # Skip small icons, avatars, or emojis
                        if any(skip in img_url.lower() for skip in ['icon', 'avatar', 'emoji', 'spacer', 'logo']):
                            continue
                        # Ensure absolute URL
                        if img_url.startswith('//'):
                            img_url = 'https:' + img_url
                        elif img_url.startswith('/'):
                            img_url = 'https://gccwalkin.com' + img_url
                        return img_url
            
            # Fallback: search any image on the whole page if none found in content div
            for img in soup.find_all('img'):
                img_url = img.get('src') or img.get('data-src')
                if img_url and 'uploads' in img_url:
                    if img_url.startswith('//'):
                        img_url = 'https:' + img_url
                    return img_url
                    
    except Exception as e:
        print(f"Error fetching image for {job_url}: {e}")
    return None

def fetch_latest_posts():
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    response = requests.get(TARGET_URL, headers=headers, timeout=15)
    if response.status_code != 200:
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    new_posts = []

    for a_tag in soup.find_all('a'):
        href = a_tag.get('href')
        text = a_tag.get_text(strip=True)
        
        if href and text and len(text) > 20:
            if "gccwalkin.com" in href and href != "https://gccwalkin.com/":
                skip_keywords = ["privacy policy", "disclaimer", "contact", "about us", "faqs", "post job", "home"]
                if not any(sk in text.lower() for sk in skip_keywords):
                    print(f"Checking poster for: {text}")
                    image_url = fetch_job_image(href)
                    
                    if image_url:
                        post_item = {
                            "title": text,
                            "link": href,
                            "image": image_url
                        }
                        if post_item not in new_posts:
                            new_posts.append(post_item)

    return new_posts[:30]

def update_json():
    latest_posts = fetch_latest_posts()
    if latest_posts:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(latest_posts, f, indent=4)
        print(f"Successfully updated {DATA_FILE} with {len(latest_posts)} poster jobs.")
    else:
        print("No poster posts fetched.")

if __name__ == "__main__":
    update_json()
