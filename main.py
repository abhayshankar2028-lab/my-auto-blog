import os
import feedparser
import datetime
import random
from huggingface_hub import InferenceClient

FEEDS = {
    "Indian Cricket": "https://indianexpress.com/section/sports/cricket/feed/",
    "Football": "https://indianexpress.com/section/sports/football/feed/",
    "Hockey": "https://indianexpress.com/section/sports/hockey/feed/",
    "Bollywood": "https://indianexpress.com/section/entertainment/bollywood/feed/",
    "Sports History": "HISTORY_MODE"
}

# High-quality Indian Sports/Culture Images
BACKUP_IMAGES = [
    "https://images.unsplash.com/photo-1531415074968-036ba1b575da?q=80&w=1000", # Cricket Ground
    "https://images.unsplash.com/photo-1540747913346-19e32dc3e97e?q=80&w=1000", # Lights/Stadium
    "https://images.unsplash.com/photo-1599423300746-b62533397364?q=80&w=1000", # Football
    "https://images.unsplash.com/photo-15176039811ef-9366f07ec0f1?q=80&w=1000"  # Indian Crowd
]

HF_TOKEN = os.environ.get("HF_TOKEN")

def run():
    print("--- STARTING INDIAN PERSPECTIVE BLOGGER ---")
    category, url = random.choice(list(FEEDS.items()))
    
    if url == "HISTORY_MODE":
        raw_title = f"Legendary Flashback: {datetime.date.today().strftime('%B %d')}"
        summary = "A moment that defined Indian pride in sports history."
        news_img = random.choice(BACKUP_IMAGES)
    else:
        feed = feedparser.parse(url)
        if not feed.entries: return
        article = feed.entries[0]
        raw_title, summary = article.title, article.summary
        news_img = article.media_content[0]['url'] if 'media_content' in article else random.choice(BACKUP_IMAGES)

    client = InferenceClient(token=HF_TOKEN)
    
    try:
        # THE "INDIAN LENS" PROMPT
        prompt = f"""
        CONTEXT: {raw_title}. SUMMARY: {summary}.
        
        TASK:
        1. FACT-CHECK: Strictly use the news provided. Do not invent scores or dates.
        2. PERSPECTIVE: Write from the viewpoint of a passionate Indian sports fan. 
           - If it's a global record, compare it to Sachin Tendulkar, Virat Kohli, or Dhyan Chand.
           - Mention how this news affects Indian fans or the Indian national team.
        3. TITLE: Create a 'Mystery' hook (e.g., 'Is Sachin's legacy finally under threat?' or 'The record India didn't see coming...').
        4. STYLE: Use a 'Human' Desi English tone (casual but expert). 350 words minimum.
        5. MULTI-IMAGE: Insert [IMAGE_HERE] twice within the text for visual breaks.
        
        FORMAT:
        TITLE: [Mystery Title]
        BODY: [350-word Indian-centric story with [IMAGE_HERE] markers]
        """

        response = client.chat_completion(
            model="meta-llama/Llama-3.2-1B-Instruct",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000
        )
        
        full_text = response.choices[0].message.content
        new_title = full_text.split("TITLE:")[1].split("BODY:")[0].strip().replace('"', '')
        body_content = full_text.split("BODY:")[1].strip()

        # Image Injection Logic
        img2 = f"![Moment]({random.choice(BACKUP_IMAGES)})"
        img3 = f"![Atmosphere]({random.choice(BACKUP_IMAGES)})"
        final_body = body_content.replace("[IMAGE_HERE]", img2, 1).replace("[IMAGE_HERE]", img3, 1)

        date_str = datetime.date.today().strftime("%Y-%m-%d")
        clean_filename = "".join(x for x in new_title if x.isalnum() or x==" ")[:25].strip().replace(" ", "-").lower()
        filename = f"_posts/{date_str}-{clean_filename}.md"

        post_data = f"---\nlayout: post\ntitle: \"{new_title}\"\ncategory: {category}\n---\n\n![Headline]({news_img})\n\n{final_body}"

        os.makedirs("_posts", exist_ok=True) 
        with open(filename, "w") as f:
            f.write(post_data)
        print(f"--- SUCCESS: Verified Indian Perspective Post Created ---")

    except Exception as e:
        print(f"--- ERROR: {str(e)} ---")

if __name__ == "__main__":
    run()
