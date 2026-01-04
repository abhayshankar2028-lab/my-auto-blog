import os
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

    # Switching to a guaranteed Chat-compatible model
    client = InferenceClient(token=HF_TOKEN)
    
    try:
        print("Requesting AI generation...")
        # Using Llama-3.2 which is natively built for this 'chat_completion' method
        response = client.chat_completion(
            model="meta-llama/Llama-3.2-1B-Instruct",
            messages=[
                {"role": "user", "content": f"Write a 150-word sports blog post about: {title}. Context: {summary}"}
            ],
            max_tokens=500
        )
        
        content = response.choices[0].message.content
        
        date_str = datetime.date.today().strftime("%Y-%m-%d")
        clean_title = "".join(x for x in title if x.isalnum() or x==" ")[:25].strip().replace(" ", "-").lower()
        filename = f"_posts/{date_str}-{clean_title}.md"

        post_data = f"---\nlayout: post\ntitle: \"{title}\"\n---\n\n{content}"

        print(f"Writing file: {filename}")
        with open(filename, "w") as f:
            f.write(post_data)
        
        print(f"--- SUCCESS: {filename} CREATED ---")

    except Exception as e:
        print(f"--- CRITICAL ERROR: {str(e)} ---")

if __name__ == "__main__":
    run()
