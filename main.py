import os
import requests
import feedparser
import datetime
from huggingface_hub import InferenceClient

# CONFIG
RSS_URL = "https://feeds.feedburner.com/TechCrunch/"
HF_TOKEN = os.environ.get("HF_TOKEN")

def run():
    print("Fetching news...")
    feed = feedparser.parse(RSS_URL)
    if not feed.entries:
        print("No news found!")
        return

    article = feed.entries[0]
    print(f"Found: {article.title}")

    # Simplified AI Prompt
    client = InferenceClient(token=HF_TOKEN)
    prompt = f"Write a 100-word blog post about: {article.title}. Content: {article.summary}"
    
    try:
        content = client.text_generation("mistralai/Mistral-7B-Instruct-v0.3", prompt, max_new_tokens=500)
        
        # Create the filename
        date_str = datetime.date.today().strftime("%Y-%m-%d")
        # Clean title for filename
        clean_title = "".join(x for x in article.title if x.isalnum() or x==" ")[:20].replace(" ", "-")
        filename = f"_posts/{date_str}-{clean_title}.md"

        # Content with Jekyll Header
        post_data = f"---\nlayout: post\ntitle: \"{article.title}\"\n---\n\n{content}"

        with open(filename, "w") as f:
            f.write(post_data)
        print(f"Successfully created {filename}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    run()
