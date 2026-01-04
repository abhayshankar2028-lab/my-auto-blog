import os
import feedparser
import datetime
import random
from huggingface_hub import InferenceClient

# CONFIG - Specialized Indian Feeds
FEEDS = {
    "Cricket": "https://indianexpress.com/section/sports/cricket/feed/",
    "Bollywood": "https://indianexpress.com/section/entertainment/bollywood/feed/"
}
HF_TOKEN = os.environ.get("HF_TOKEN")

def run():
    print("--- STARTING INDIAN NEWS BOT ---")
    
    # Randomly pick between Cricket and Bollywood
    category, url = random.choice(list(FEEDS.items()))
    print(f"Checking category: {category}")
    
    feed = feedparser.parse(url)
    if not feed.entries:
        print(f"No {category} news found.")
        return
        
    article = feed.entries[0]
    title = article.title
    summary = article.summary
    print(f"Found: {title}")

    client = InferenceClient(token=HF_TOKEN)
    
    try:
        print("Requesting AI generation...")
        response = client.chat_completion(
            model="meta-llama/Llama-3.2-1B-Instruct",
            messages=[
                {"role": "system", "content": f"You are a trendy Indian blogger specializing in {category}."},
                {"role": "user", "content": f"Write a 150-word engaging Indian blog post about: {title}. Context: {summary}. Use a mix of formal and casual 'Desi' style."}
            ],
            max_tokens=500
        )
        
        content = response.choices[0].message.content
        date_str = datetime.date.today().strftime("%Y-%m-%d")
        clean_title = "".join(x for x in title if x.isalnum() or x==" ")[:25].strip().replace(" ", "-").lower()
        filename = f"_posts/{date_str}-{clean_title}.md"

        # Jekyll header
        post_data = f"---\nlayout: post\ntitle: \"{title}\"\ncategory: {category}\n---\n\n{content}"

        os.makedirs("_posts", exist_ok=True) 
        with open(filename, "w") as f:
            f.write(post_data)
        
        print(f"--- SUCCESS: {category} Post Created ---")

    except Exception as e:
        print(f"--- ERROR: {str(e)} ---")

if __name__ == "__main__":
    run()
