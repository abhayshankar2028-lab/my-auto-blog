import os
import feedparser
import datetime
import random
import re
from huggingface_hub import InferenceClient

# CONFIG - Global & Indian Feeds
FEEDS = {
    "Cricket": "https://indianexpress.com/section/sports/cricket/feed/",
    "General Sports": "https://indianexpress.com/section/sports/feed/",
    "Bollywood": "https://indianexpress.com/section/entertainment/bollywood/feed/",
    "Hollywood": "https://indianexpress.com/section/entertainment/hollywood/feed/",
    "Reviews": "https://indianexpress.com/section/entertainment/movie-review/feed/",
    "Sports History": "HISTORY_MODE"
}

FALLBACK_IMAGE = "https://images.unsplash.com/photo-1504711434969-e33886168f5c?q=80&w=1200"
HF_TOKEN = os.environ.get("HF_TOKEN")

def extract_content(text, tag, next_tag=None):
    """Safely extracts text between markers used by the AI."""
    try:
        start = text.find(tag) + len(tag)
        if next_tag:
            end = text.find(next_tag)
            return text[start:end].strip()
        return text[start:].strip()
    except:
        return ""

def run():
    print("--- STARTING HARSHA-STYLE SEO BLOGGER ---")
    category, url = random.choice(list(FEEDS.items()))
    
    if url == "HISTORY_MODE":
        raw_title = f"A Moment in Time: {datetime.date.today().strftime('%B %d')}"
        summary = "A walk down memory lane in the world of legends."
        news_img = FALLBACK_IMAGE
    else:
        feed = feedparser.parse(url)
        if not feed.entries: return
        article = feed.entries[0]
        raw_title, summary = article.title, article.summary
        news_img = article.media_content[0]['url'] if (hasattr(article, 'media_content') and len(article.media_content) > 0) else FALLBACK_IMAGE

    client = InferenceClient(token=HF_TOKEN)
    
    try:
        # THE HARSHA BHOGLE PROMPT
        prompt = f"""
        ACT AS: Harsha Bhogle (The Voice of Cricket). 
        NEWS: {raw_title}. 
        SUMMARY: {summary}.
        CATEGORY: {category}.
        
        TASK:
        1. TITLE: Create a mystery/hook title (Max 10 words).
        2. BODY: Elaborate the news in 100-200 words using poetic metaphors and insightful storytelling.
        3. SEO_DESC: A crisp 150-character summary for Google.
        4. TAGS: 3 relevant keywords.
        
        FORMAT:
        TITLE: [Title]
        SEO_DESC: [Description]
        TAGS: [Tag1, Tag2, Tag3]
        BODY: [The Story]
        """

        response = client.chat_completion(
            model="meta-llama/Llama-3.2-1B-Instruct",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=800
        )
        
        res_text = response.choices[0].message.content

        # SAFE PARSING
        new_title = extract_content(res_text, "TITLE:", "SEO_DESC:").replace('"', '')
        seo_desc = extract_content(res_text, "SEO_DESC:", "TAGS:").replace('"', '')
        tags_raw = extract_content(res_text, "TAGS:", "BODY:")
        content = extract_content(res_text, "BODY:")

        # Clean tags into a Python list
        tags_list = [t.strip() for t in tags_raw.replace('[', '').replace(']', '').split(',')]

        # Date and Filename logic
        date_str = datetime.date.today().strftime("%Y-%m-%d")
        clean_fn = re.sub(r'[^a-zA-Z0-9\s]', '', new_title).strip().replace(" ", "-").lower()[:30]
        filename = f"_posts/{date_str}-{clean_fn}.md"

        # SEO-OPTIMIZED FRONT MATTER (Using block scalar '|' for description safety)
        post_data = f"""---
layout: post
title: "{new_title[:100]}"
description: |
  {seo_desc[:160]}
category: "{category}"
tags: {tags_list[:5]}
image: "{news_img}"
---

![{new_title}]({news_img})

{content}
"""

        os.makedirs("_posts", exist_ok=True) 
        with open(filename, "w") as f:
            f.write(post_data)
        print(f"--- SUCCESS: {filename} created successfully ---")

    except Exception as e:
        print(f"--- FAILED TO PROCESS: {str(e)} ---")

if __name__ == "__main__":
    run()
