import os
import requests
import feedparser
import datetime
from huggingface_hub import InferenceClient

RSS_URL = "https://www.skysports.com/rss/12040"
HF_TOKEN = os.environ.get("HF_TOKEN")

def run():
    print("--- STARTING SCRIPT ---")
    feed = feedparser.parse(RSS_URL)
    
    if not feed.entries:
        print("No news found.")
        return
        
    article = feed.entries[0]
    title = article.title
    summary = article.summary
    print(f"Article Found: {title}")

    client = InferenceClient(token=HF_TOKEN)
    
    try:
        print("Requesting AI generation via Chat interface...")
        # FIXED: Using chat_completion because the model now requires 'conversational' task
        response = client.chat_completion(
            model="mistralai/Mistral-7B-Instruct-v0.3",
            messages=[
                {"role": "system", "content": "You are a professional sports journalist."},
                {"role": "user", "content": f"Write a 150-word blog post about: {title}. Context: {summary}"}
            ],
            max_tokens=500
        )
        
        content = response.choices[0].message.content
        
        date_str = datetime.date.today().strftime("%Y-%m-%d")
        clean_title = "".join(x for x in title if x.isalnum() or x==" ")[:20].strip().replace(" ", "-").lower()
        filename = f"_posts/{date_str}-{clean_title}.md"

        post_data = f"---\nlayout: post\ntitle: \"{title}\"\n---\n\n{content}"

        print(f"Attempting to write file: {filename}")
        with open(filename, "w") as f:
            f.write(post_data)
        
        if os.path.exists(filename):
            print(f"--- SUCCESS: {filename} CREATED ---")

    except Exception as e:
        print(f"--- CRITICAL ERROR: {str(e)} ---")

if __name__ == "__main__":
    run()
