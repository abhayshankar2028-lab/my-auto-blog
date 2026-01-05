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
    print("--- STARTING NEWS BOT WITH IMAGES ---")
    category, url = random.choice(list(FEEDS.items()))
    feed = feedparser.parse(url)
    
    if not feed.entries:
        return
        
    article = feed.entries[0]
    title = article.title
    summary = article.summary
    
    # --- IMAGE EXTRACTION LOGIC ---
    image_url = ""
    # Look for image in media_content or links
    if 'media_content' in article:
        image_url = article.media_content[0]['url']
    elif 'links' in article:
        for link in article.links:
            if 'image' in link.get('type', ''):
                image_url = link.get('href', '')
    
    client = InferenceClient(token=HF_TOKEN)
    
    try:
        response = client.chat_completion(
            model="meta-llama/Llama-3.2-1B-Instruct",
            messages=[
                {"role": "system", "content": f"You are a professional {category} blogger."},
                {"role": "user", "content": f"Write a 150-word post about: {title}. Summary: {summary}"}
            ],
            max_tokens=400
        )
        
        content = response.choices[0].message.content
        date_str = datetime.date.today().strftime("%Y-%m-%d")
        clean_title = "".join(x for x in title if x.isalnum() or x==" ")[:25].strip().replace(" ", "-").lower()
        filename = f"_posts/{date_str}-{clean_title}.md"

        # Add image to the post using Markdown syntax
        image_markdown = f"![{title}]({image_url})\n\n" if image_url else ""
        
        post_data = f"---\nlayout: post\ntitle: \"{title}\"\n---\n\n{image_markdown}{content}"

        os.makedirs("_posts", exist_ok=True) 
        with open(filename, "w") as f:
            f.write(post_data)
        print(f"--- SUCCESS: {category} Post Created with Image ---")

    except Exception as e:
        print(f"--- ERROR: {str(e)} ---")

if __name__ == "__main__":
    run()
