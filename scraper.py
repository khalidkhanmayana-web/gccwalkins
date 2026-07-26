import json
import os
import requests
from bs4 import BeautifulSoup

TARGET_URL = "https://gccwalkin.com/"
DATA_FILE = "posts.json"

def fetch_latest_posts():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5"
    }
    
    try:
        response = requests.get(TARGET_URL, headers=headers, timeout=15)
        print(f"HTTP Status Code: {response.status_code}")
        if response.status_code != 200:
            return []
    except Exception as e:
        print(f"Request error: {e}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    new_posts = []

    # Target the specific Newsup/WordPress heading links where job titles are posted
    # Looking for titles inside headings or post entry wrappers
    for a_tag in soup.find_all('a'):
        href = a_tag.get('href')
        text = a_tag.get_text(strip=True)
        
        # Validation checks to ensure we capture actual job posts and avoid menu/footer links
        if href and text and len(text) > 20:
            if "gccwalkin.com" in href and href != "https://gccwalkin.com/":
                # Exclude standard navigation/footer links
                skip_keywords = ["privacy policy", "disclaimer", "contact", "about us", "faqs", "post job", "home"]
                if not any(sk in text.lower() for sk in skip_keywords):
                    post_item = {
                        "title": text,
                        "link": href
                    }
                    if post_item not in new_posts:
                        new_posts.append(post_item)

    print(f"Successfully scraped {len(new_posts)} posts.")
    return new_posts[:50]

def update_json():
    existing_posts = []
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            try:
                existing_posts = json.load(f)
            except json.JSONDecodeError:
                existing_posts = []

    existing_links = {p["link"] for p in existing_posts}
    latest_posts = fetch_latest_posts()
    
    added_count = 0
    for post in latest_posts:
        if post["link"] not in existing_links:
            existing_posts.insert(0, post)
            added_count += 1

    if added_count > 0:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(existing_posts, f, indent=4)
        print(f"Added {added_count} new posts to {DATA_FILE}.")
    else:
        print("No new posts to add.")

if __name__ == "__main__":
    update_json()
