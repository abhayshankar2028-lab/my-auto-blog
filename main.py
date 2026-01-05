import os
import feedparser
import datetime
import random
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

def run():
    print("--- STARTING HARSHA-STYLE SEO BLOGGER ---")
    category, url = random.choice(list(FEEDS.items()))
    
    if url == "HISTORY_MODE":
        raw_title = f"Legacy Remembered: {datetime.date.today().strftime('%B %d')}"
        summary = "A moment that defined the very spirit of the game."
        news_img = FALLBACK_IMAGE
    else:
        feed = feedparser.parse(url)
        if not feed.entries: return
        article = feed.entries[0]
        raw_title, summary = article.title, article.summary
        news_img = article.media_content[0]['url'] if 'media_content' in article else FALLBACK_IMAGE

    client = InferenceClient(token=HF_TOKEN)
    
    try:
        # THE SEO + HARSHA PROMPT
        prompt = f"""
        NEWS: {raw_title}. 
        SUMMARY: {summary}.
        CATEGORY: {category}.
        
        TASK:
        1. ACT AS: Harsha Bhogle. Be poetic, articulate, and provide an Indian fan's perspective.
        2. MYSTERY TITLE: A high-CTR title (e.g., 'Sachin's record in danger?' or 'The Hollywood secret India missed').
        3. BODY: Elaborate the news in 100-200 words. Use metaphors and deep insights.
        4. SEO DESCRIPTION: Write a 150-character summary for Google search results.
        5. TAGS: Provide 3-5 relevant keywords separated by commas.
        
        FORMAT:
        TITLE: [Mystery Title]
        SEO_DESC: [Meta Description]
        TAGS: [Keywords]
        BODY: [100-200 words of Bhogle-style story]
        """

        response = client.chat_completion(
            model="meta-llama/Llama-3.2-1B-Instruct",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=600
        )
        
        full_text = response.choices[0].message.content
        new_title = full_text.split("TITLE:")[1].split("SEO_DESC:")[0].strip().replace('"', '')
        seo_desc = full_text.split("SEO_DESC:")[1].split("TAGS:")[0].strip()
        keywords = full_text.split("TAGS:")[1].split("BODY:")[0].strip()
        content = full_text.split("BODY:")[1].strip()

        date_str = datetime.date.today().strftime("%Y-%m-%d")
        # Clean URL for SEO
        clean_fn = "".join(x for x in new_title if x.isalnum() or x==" ")[:30].strip().replace(" ", "-").lower()
        filename = f"_posts/{date_str}-{clean_fn}.md"

        # SEO-OPTIMIZED FRONT MATTER
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
        print(f"--- SUCCESS: {category} Post (SEO Optimized) Created ---")

    except Exception as e:
        print(f"--- ERROR: {str(e)} ---")

if __name__ == "__main__":
    run()
