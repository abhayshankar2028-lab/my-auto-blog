import os
import requests
import feedparser
import datetime
from huggingface_hub import InferenceClient

# Use a reliable sports feed
RSS_URL = "https://newsrss.bbc.co.uk/rss/sport_api/800/rss.xml"
HF_TOKEN = os.environ.get("HF_TOKEN")

def run():
    feed = feedparser.parse(RSS_URL)
    if not feed.entries:
        return

    article = feed.entries[0]
    client = InferenceClient(token=HF_TOKEN)
    prompt = f"Write a 150-word sports news report about: {article.title}. Summary: {article.summary}"
    
    try:
        content = client.text_generation("mistralai/Mistral-7B-Instruct-v0.3", prompt, max_new_tokens=500)
        date_str = datetime.date.today().strftime("%Y-%m-%d")
        clean_title = "".join(x for x in article.title if x.isalnum() or x==" ")[:30].strip().replace(" ", "-").lower()
        filename = f"_posts/{date_str}-{clean_title}.md"

        post_data = f"---\nlayout: post\ntitle: \"{article.title}\"\ndate: {date_str}\n---\n\n{content}"

        with open(filename, "w") as f:
            f.write(post_data)
        print("Success")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    run()
