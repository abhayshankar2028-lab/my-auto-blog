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

# Secondary images to make the blog look rich
BACKUP_IMAGES = [
    "https://images.unsplash.com/photo-1531415074968-036ba1b575da?auto=format&fit=crop&q=80&w=1000", # Cricket
    "https://images.unsplash.com/photo-1574629810360-7efbbe195018?auto=format&fit=crop&q=80&w=1000", # Football
    "https://images.unsplash.com/photo-15176039811ef-9366f07ec0f1?auto=format&fit=crop&q=80&w=1000", # Stadium
    "https://images.unsplash.com/photo-1485846234645-a62644f84728?auto=format&fit=crop&q=80&w=1000"  # Movie/Cinema
]

HF_TOKEN = os.environ.get("HF_TOKEN")

def run():
    print("--- STARTING MULTI-IMAGE MYSTERY BLOGGER ---")
    category, url = random.choice(list(FEEDS.items()))
    
    # Fetching the news
    if url == "HISTORY_MODE":
        raw_title = f"On this day in history: {datetime.date.today().strftime('%B %d')}"
        summary = "An incredible moment that changed Indian sports forever."
        news_img = random.choice(BACKUP_IMAGES)
    else:
        feed = feedparser.parse(url)
        if not feed.entries: return
        article = feed.entries[0]
        raw_title, summary = article.title, article.summary
        news_img = article.media_content[0]['url'] if 'media_content' in article else random.choice(BACKUP_IMAGES)

    client = InferenceClient(token=HF_TOKEN)
    
    try:
        # THE DRAMATIC PROMPT
        prompt = f"""
        ACT AS: A top Indian sports influencer. 
        TOPIC: {raw_title}
        CONTEXT: {summary}
        
        STRICT RULES:
        1. TITLE: Must be a cliffhanger mystery (e.g., 'Is Sachin's record finally in danger?' or 'The one player nobody expected to rise...').
        2. LANGUAGE: Extremely human, emotional, and casual ('Desi' style). Use 'Chalo', 'Listen up', 'Can you believe it?'.
        3. WORD COUNT: 350 words minimum. Maintain the factual essence but add spicy opinions.
        4. STRUCTURE: Break it into 3 parts. After Part 1 and Part 2, write [IMAGE_HERE].
        
        FORMAT:
        TITLE: [Mystery Title]
        BODY: [350-word story with [IMAGE_HERE] markers]
        """

        response = client.chat_completion(
            model="meta-llama/Llama-3.2-1B-Instruct",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000
        )
        
        full_text = response.choices[0].message.content
        new_title = full_text.split("TITLE:")[1].split("BODY:")[0].strip().replace('"', '')
        body_content = full_text.split("BODY:")[1].strip()

        # Insert 2nd and 3rd images into the markers
        img2 = f"![Action]({random.choice(BACKUP_IMAGES)})"
        img3 = f"![Details]({random.choice(BACKUP_IMAGES)})"
        
        final_body = body_content.replace("[IMAGE_HERE]", img2, 1).replace("[IMAGE_HERE]", img3, 1)

        # File creation
        date_str = datetime.date.today().strftime("%Y-%m-%d")
        clean_filename = "".join(x for x in new_title if x.isalnum() or x==" ")[:25].strip().replace(" ", "-").lower()
        filename = f"_posts/{date_str}-{clean_filename}.md"

        post_data = f"---\nlayout: post\ntitle: \"{new_title}\"\n---\n\n![Headline]({news_img})\n\n{final_body}"

        os.makedirs("_posts", exist_ok=True) 
        with open(filename, "w") as f:
            f.write(post_data)
        print(f"--- SUCCESS: {category} Post with 3 Images Created ---")

    except Exception as e:
        print(f"--- ERROR: {str(e)} ---")

if __name__ == "__main__":
    run()
