import os
import requests
import feedparser
import datetime
import re
from huggingface_hub import InferenceClient

# --- CONFIG ---
# Using TechCrunch RSS for tech news
RSS_URL = "https://techcrunch.com/feed/"
HF_TOKEN = os.environ["HF_TOKEN"]

def clean_filename(title):
    # Converts "Hello World!" to "hello-world" for the filename
    return re.sub(r'[^a-zA-Z0-9]', '-', title).lower()

def get_news():
    feed = feedparser.parse(RSS_URL)
    if not feed.entries:
        return None
    return feed.entries[0]

def generate_post(article):
    client = InferenceClient(token=HF_TOKEN)
    model = "mistralai/Mistral-7B-Instruct-v0.3"
    
    prompt = f"""
    Act as a professional tech blogger. Write a blog post based on this news.
    
    Rules:
    1. Title: Catchy and SEO optimized.
    2. Format: Use Markdown (## for headers, * for bullets).
    3. Length: Short and engaging (approx 300 words).
    4. Structure: Intro -> Key Details -> Why it Matters.
    
    News Title: {article.title}
    News Summary: {article.summary}
    """
    
    try:
        response = client.text_generation(model, prompt, max_new_tokens=1000, temperature=0.7)
        return response
    except Exception as e:
        print(e)
        return None

if __name__ == "__main__":
    print("Fetching news...")
    article = get_news()
    
    if article:
        print(f"Generating blog for: {article.title}")
        content = generate_post(article)
        
        if content:
            # Jekyll requires a specific filename format: YYYY-MM-DD-title.md
            date_str = datetime.date.today().strftime("%Y-%m-%d")
            filename = f"_posts/{date_str}-{clean_filename(article.title)[:30]}.md"
            
            # Jekyll requires "Front Matter" at the top of the file
            final_content = f"""---
layout: post
title: "{article.title.replace('"', "'")}"
date: {date_str}
---

{content}

---
*Source: [Read original article]({article.link})*
"""
            
            # Write the file
            with open(filename, "w") as f:
                f.write(final_content)
            print(f"Saved to {filename}")
        else:
            print("AI generation failed")
    else:
        print("No news found")
