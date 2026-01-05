import os
import feedparser
import datetime
import random
import re
from huggingface_hub import InferenceClient

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
    """Safely extracts text between two tags."""
    try:
        start = text.find(tag) + len(tag)
        if next_tag:
            end = text.find(next_tag)
            return text[start:end].strip().replace('"', '')
        return text[start:].strip()
    except:
        return "Insightful update from the world of entertainment."

def run():
    print("--- STARTING HARSHA-STYLE SEO BLOGGER V2 ---")
    category, url = random.choice(list(FEEDS.items()))
    
    if url == "HISTORY_MODE":
        raw_title = f"A Moment in Time: {datetime.date.today().strftime('%B %d')}"
        summary = "An event that reminded us why we love the game/cinema."
        news_img = FALLBACK_IMAGE
    else:
        feed = feedparser.parse(url)
        if not feed.entries: return
        article = feed.entries[0]
        raw_title, summary = article.title, article.summary
        # SAFE IMAGE CHECK: Ensure media_content exists and is NOT empty
        news_img = article.media_content[0]['url'] if (hasattr(article, 'media_content') and len(article.media_content) > 0) else FALLBACK_IMAGE

    client = InferenceClient(token=HF_TOKEN)
    
    try:
        prompt = f"""
        NEWS: {raw_title}. 
        SUMMARY: {summary}.
        CATEGORY: {category}.
        
        TASK:
        1. ACT AS: Harsha Bhogle. Be poetic, articulate, and use 'word pictures'.
        2. MYSTERY TITLE: A high-CTR title (e.g. 'Is the legacy of this superstar in danger?').
        3. BODY: 100-200 words of storytelling.
        4. SEO_DESC: A 150-character search snippet.
        5. TAGS: 3-5 keywords.
        
        FORMAT:
        TITLE: [Title]
        SEO_DESC: [Description]
        TAGS: [Keywords]
        BODY: [Story]
        """

        response = client.chat_completion(
            model="meta-llama/Llama-3.2-1B-Instruct",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=600
        )
        
        res_text = response.choices[0].message.content

        # SAFE PARSING using the helper function
        new_title = extract_content(res_text, "TITLE:", "SEO_DESC:")
        seo_desc = extract_content(res_text, "SEO_DESC:", "TAGS:")
        keywords = extract_content(res_text, "TAGS:", "BODY:")
        content = extract_content(res_text, "BODY:")

        # Clean filename
        date_str = datetime.date.today().strftime("%Y-%m-%d")
        clean_fn = re.sub(r'[^a-zA-Z0-9\s]', '', new_title).strip().replace(" ", "-").lower()[:30]
        filename = f"_posts/{date_str}-{clean_fn}.md"

        post_data = f"""---
layout: post
title: "{new_title}"
description: "{seo_desc}"
category: {category}
tags: [{keywords}]
image: {news_img}
---

![{new_title}]({news_img})

{content}"""

        os.makedirs("_posts", exist_ok=True) 
        with open(filename, "w") as f:
            f.write(post_data)
        print(f"--- SUCCESS: {category} Post Created ---")

    except Exception as e:
        print(f"--- FAILED TO PROCESS: {str(e)} ---")

if __name__ == "__main__":
    run()
