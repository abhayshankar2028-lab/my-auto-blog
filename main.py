import os
import feedparser
import datetime
from huggingface_hub import InferenceClient

# CONFIG - Cricket News Feed
RSS_URL = "https://www.espncricinfo.com/rss/content/story/feeds/0.xml"
HF_TOKEN = os.environ.get("HF_TOKEN")

def run():
    print("--- STARTING CRICKET BLOGGER ---")
    feed = feedparser.parse(RSS_URL)
    
    if not feed.entries:
        print("No cricket news found at the moment.")
        return
        
    article = feed.entries[0]
    title = article.title
    summary = article.summary
    print(f"Latest News Found: {title}")

    # Use Llama-3.2-1B-Instruct for guaranteed compatibility
    client = InferenceClient(token=HF_TOKEN)
    
    try:
        print("Requesting AI to write match report...")
        response = client.chat_completion(
            model="meta-llama/Llama-3.2-1B-Instruct",
            messages=[
                {"role": "system", "content": "You are a professional cricket commentator and journalist."},
                {"role": "user", "content": f"Write a 150-word cricket news update about: {title}. Context: {summary}. Use a professional tone."}
            ],
            max_tokens=500
        )
        
        content = response.choices[0].message.content
        
        # File naming logic for Jekyll
        date_str = datetime.date.today().strftime("%Y-%m-%d")
        clean_title = "".join(x for x in title if x.isalnum() or x==" ")[:25].strip().replace(" ", "-").lower()
        filename = f"_posts/{date_str}-{clean_title}.md"

        # Jekyll Front Matter (Required for the website to show the post)
        post_data = f"---\nlayout: post\ntitle: \"{title}\"\ndate: {date_str}\n---\n\n{content}"

        print(f"Saving file: {filename}")
        # Ensure the _posts folder is targeted correctly
        os.makedirs("_posts", exist_ok=True) 
        with open(filename, "w") as f:
            f.write(post_data)
        
        print(f"--- SUCCESS: {filename} CREATED ---")

    except Exception as e:
        print(f"--- CRITICAL ERROR: {str(e)} ---")

if __name__ == "__main__":
    run()
