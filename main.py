import os
import feedparser
import datetime
import random
from huggingface_hub import InferenceClient

# CONFIG - Expanded Feeds
FEEDS = {
    "Indian Cricket": "https://indianexpress.com/section/sports/cricket/feed/",
    "Football": "https://indianexpress.com/section/sports/football/feed/",
    "Hockey": "https://indianexpress.com/section/sports/hockey/feed/",
    "Bollywood": "https://indianexpress.com/section/entertainment/bollywood/feed/",
    "Sports History": "HISTORY_MODE" # Special flag for historical content
}
HF_TOKEN = os.environ.get("HF_TOKEN")

def run():
    print("--- STARTING MULTI-TOPIC BLOGGER ---")
    category, url = random.choice(list(FEEDS.items()))
    print(f"Selected Category: {category}")
    
    image_url = ""
    raw_title = ""
    summary = ""

    # Logic for Live News vs. History
    if url == "HISTORY_MODE":
        raw_title = f"Indian Sports History: {datetime.date.today().strftime('%B %d')}"
        summary = "Generate a significant event in Indian Cricket, Hockey, or Football history that happened on this day."
    else:
        feed = feedparser.parse(url)
        if not feed.entries: return
        article = feed.entries[0]
        raw_title = article.title
        summary = article.summary
        
        # Image extraction
        if 'media_content' in article:
            image_url = article.media_content[0]['url']
        elif 'links' in article:
            for link in article.links:
                if 'image' in link.get('type', ''):
                    image_url = link.get('href', '')

    client = InferenceClient(token=HF_TOKEN)
    
    try:
        # THE HUMAN PROMPT
        prompt = f"""
        ACT AS: An Indian sports and culture enthusiast with a massive following.
        TOPIC: {raw_title}
        CONTEXT: {summary}
        CATEGORY: {category}
        
        TASK:
        1. CREATE A SURPRISE TITLE: Use a mystery hook or a 'Did you know?' vibe.
        2. WRITE A 350-WORD HUMAN POST: 
           - If it's History, tell a nostalgic, legendary story.
           - If it's News, be energetic and opinionated.
           - Use 'Desi' English (e.g., 'What a match!', 'Historic moment, guys!').
           - Focus on the human emotion behind the sport/movie.
        
        FORMAT:
        TITLE: [Your Mystery Title]
        BODY: [Your 350-word story]
        """

        response = client.chat_completion(
            model="meta-llama/Llama-3.2-1B-Instruct",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=900
        )
        
        full_text = response.choices[0].message.content
        
        try:
            new_title = full_text.split("TITLE:")[1].split("BODY:")[0].strip().replace('"', '')
            content = full_text.split("BODY:")[1].strip()
        except:
            new_title = f"A Legend Unfolds: {raw_title}"
            content = full_text

        date_str = datetime.date.today().strftime("%Y-%m-%d")
        clean_filename = "".join(x for x in new_title if x.isalnum() or x==" ")[:25].strip().replace(" ", "-").lower()
        filename = f"_posts/{date_str}-{clean_filename}.md"

        # Use a default sports image if History mode has no image
        if not image_url and url == "HISTORY_MODE":
            image_url = "https://images.unsplash.com/photo-1540747913346-19e32dc3e97e?q=80&w=1000"

        image_markdown = f"![{category}]({image_url})\n\n" if image_url else ""
        post_data = f"---\nlayout: post\ntitle: \"{new_title}\"\ncategory: {category}\n---\n\n{image_markdown}{content}"

        os.makedirs("_posts", exist_ok=True) 
        with open(filename, "w") as f:
            f.write(post_data)
        print(f"--- SUCCESS: {category} Post Created ---")

    except Exception as e:
        print(f"--- ERROR: {str(e)} ---")

if __name__ == "__main__":
    run()
