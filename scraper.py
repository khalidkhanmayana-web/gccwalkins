import json
import os
import requests
from bs4 import BeautifulSoup

TARGET_URL = "https://gccwalkin.com/"
DATA_FILE = "posts.json"

def fetch_latest_posts():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    response = requests.get(TARGET_URL, headers=headers)
    if response.status_code != 200:
        print(f"Failed to fetch website. Status code: {response.status_code}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    new_posts = []

    # Target standard WordPress article/post links and headings on the page
    # This selector looks for anchor tags inside headings or post wrappers
    articles = soup.find_all(['article', 'div'], class_=lambda x: x and ('post' in x or 'entry' in x or 'card' in x))
    
    # Fallback search if specific containers aren't caught: look for all links inside main content areas
    for item in soup.find_all('a'):
        href = item.get('href')
        text = item.get_text(strip=True)
        
        # Filter for actual job posting links (usually containing hiring, job, requirement, interview)
        if href and text and len(text) > 15:
            keywords = ["hiring", "requirement", "interview", "dubai", "saudi", "abu dhabi", "qatar", "kuwait", "oman", "walk-in", "job"]
            if any(kw in text.lower() for kw in keywords):
                if not href.startswith("http"):
                    continue
                
                post_item = {
                    "title": text,
                    "link": href
                }
                if post_item not in new_posts:
                    new_posts.append(post_item)

    return new_posts[:40] # Keep the top 40 freshest unique job links

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
        print(f"Added {added_count} new posts.")
    else:
        print("No new posts found.")

if __name__ == "__main__":
    update_json()
