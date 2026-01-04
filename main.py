import os
import requests
import feedparser
import datetime
from huggingface_hub import InferenceClient

# CONFIG - Using BBC Sports for reliable data
RSS_URL = "https://newsrss.bbc.co.uk/rss/sport_api/800/rss.xml"
HF_TOKEN = os.environ.get("HF_TOKEN")

def run():
    print("Step 1: Fetching news...")
    feed = feedparser.parse(RSS_URL)
    
    if not feed.entries:
        print("Error: No news entries found in the RSS feed.")
        return

    article = feed.entries[0]
    print(f"Step 2: Found article: {article.title}")

    # Brain: Hugging Face AI
    print("Step 3: Asking AI to write the post...")
    client = InferenceClient(token=HF_TOKEN)
    prompt = f"Write a professional 150-word sports blog post about: {article.title}. Summary: {article.summary}"
    
    try:
        # Using a reliable model
        content = client.text_generation("mistralai/Mistral-7B-Instruct-v0.3", prompt, max_new_tokens=500)
        
        # Step 4: Create the filename with YYYY-MM-DD format
        date_str = datetime.date.today().strftime("%Y-%m-%d")
        clean_title = "".join(x for x in article.title if x.isalnum() or x==" ")[:30].strip().replace(" ", "-").lower()
        filename = f"_posts/{date_str}-{clean_title}.md"

        # Jekyll Front Matter (Required for GitHub Pages)
        post_data = f"---\nlayout: post\ntitle: \"{article.title}\"\ndate: {date_str}\n---\n\n{content}"

        print(f"Step 5: Saving file to {filename}")
        with open(filename, "w") as f:
            f.write(post_data)
        print("SUCCESS: File created locally!")
        
    except Exception as e:
        print(f"AI Error: {e}")

if __name__ == "__main__":
    run()
- name: Commit and Push Changes
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
          git add _posts/*.md
          git commit -m "New sports post" || echo "Nothing to commit"
          git push
