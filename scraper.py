import json
import os
import requests
from bs4 import BeautifulSoup

TARGET_URL = "https://gccwalkin.com/"
DATA_FILE = "posts.json"

def fetch_latest_posts():
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    response = requests.get(TARGET_URL, headers=headers)
    if response.status_code != 200:
        print("Failed to fetch website.")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    new_posts = []

    articles = soup.find_all('div', class_='bs-sec-post')
    for article in articles:
        title_tag = article.find('h3') or article.find('a')
        if title_tag and title_tag.find('a'):
            title = title_tag.get_text(strip=True)
            link = title_tag.find('a')['href']
            
            new_posts.append({
                "title": title,
                "link": link
            })
    return new_posts

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
