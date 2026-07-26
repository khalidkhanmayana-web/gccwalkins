import json
import os
import requests
from bs4 import BeautifulSoup

TARGET_URL = "https://gccwalkin.com/"
DATA_FILE = "posts.json"

def fetch_job_details(job_url):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    try:
        res = requests.get(job_url, headers=headers, timeout=10)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            # Look for standard WordPress content containers
            content_div = soup.find('div', class_='entry-content') or soup.find('div', class_='bs-content') or soup.find('article')
            if content_div:
                for element in content_div(["script", "style", "iframe", "header", "footer"]):
                    element.decompose()
                return content_div.decode_contents()
            else:
                # Fallback: grab all paragraphs on the page
                paragraphs = soup.find_all('p')
                if paragraphs:
                    return "".join([str(p) for p in paragraphs])
    except Exception as e:
        print(f"Error fetching details for {job_url}: {e}")
    return "<p>Please visit the official source for full walk-in interview details and venue requirements.</p>"

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
                    print(f"Fetching details for: {text}")
                    details_html = fetch_job_details(href)
                    
                    post_item = {
                        "title": text,
                        "link": href,
                        "content": details_html
                    }
                    if post_item not in new_posts:
                        new_posts.append(post_item)

    return new_posts[:30]

def update_json():
    # Clear out old posts that lack content or reset the file fresh
    latest_posts = fetch_latest_posts()
    
    if latest_posts:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(latest_posts, f, indent=4)
        print(f"Successfully updated {DATA_FILE} with {len(latest_posts)} posts including full content.")
    else:
        print("No posts fetched.")

if __name__ == "__main__":
    update_json()
