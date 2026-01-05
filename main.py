import os
import feedparser
import datetime
import random
from huggingface_hub import InferenceClient

# CONFIG - Expanded Global & Indian Feeds
FEEDS = {
    "Cricket": "https://indianexpress.com/section/sports/cricket/feed/",
    "General Sports": "https://indianexpress.com/section/sports/feed/",
    "Bollywood": "https://indianexpress.com/section/entertainment/bollywood/feed/",
    "Hollywood": "https://indianexpress.com/section/entertainment/hollywood/feed/",
    "Reviews": "https://indianexpress.com/section/entertainment/movie-review/feed/",
    "Sports History": "HISTORY_MODE"
}

FALLBACK_IMAGE = "https://images.unsplash.com/photo-1504711434969-e33886168f5c?q=80&w=1200"
HF_TOKEN = os.environ.get("HF_TOKEN")

def run():
    print("--- STARTING HARSHA-STYLE GLOBAL BLOGGER ---")
    category, url = random.choice(list(FEEDS.items()))
    
    # Data Fetching
    if url == "HISTORY_MODE":
        raw_title = f"A Moment Frozen in Time: {datetime.date.today().strftime('%B %d')}"
        summary = "An event that reminded us why we love the beautiful game/cinema."
        news_img = FALLBACK_IMAGE
    else:
        feed = feedparser.parse(url)
        if not feed.entries: return
        article = feed.entries[0]
        raw_title, summary = article.title, article.summary
        news_img = article.media_content[0]['url'] if 'media_content' in article else FALLBACK_IMAGE

    client = InferenceClient(token=HF_TOKEN)
    
    try:
        # THE HARSHA BHOGLE PERSONA PROMPT
        prompt = f"""
        NEWS: {raw_title}. 
        CONTEXT: {summary}.
        CATEGORY: {category}.
        
        TASK:
        1. ACT AS: Harsha Bhogle. Be articulate, poetic, and insightful. Use 'word pictures'.
        2. MYSTERY TITLE: Create a cliffhanger (e.g. 'Is the legacy of this superstar in danger?' or 'The one thing nobody noticed about...').
        3. CONTENT: Elaborate on the news and provide the information in 100-200 words ONLY.
        4. INDIAN PERSPECTIVE: Even if it's Hollywood, tell us why it matters to the Indian viewer.
        5. FACT-CHECK: Strictly stick to the news essence provided.
        
        STYLE GUIDE:
        - Start with an observation like 'I've often thought...' or 'There's a certain joy in...'
        - Use metaphors. 
        - If it's a Movie Review, judge it with grace and insight.
        
        FORMAT:
        TITLE: [Mystery Title]
        BODY: [100-200 words of Harsha-style storytelling]
        """

        response = client.chat_completion(
            model="meta-llama/Llama-3.2-1B-Instruct",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500
        )
        
        full_text = response.choices[0].message.content
        new_title = full_text.split("TITLE:")[1].split("BODY:")[0].strip().replace('"', '')
        content = full_text.split("BODY:")[1].strip()

        # Filename & Save
        date_str = datetime.date.today().strftime("%Y-%m-%d")
        clean_fn = "".join(x for x in new_title if x.isalnum() or x==" ")[:25].strip().replace(" ", "-").lower()
        filename = f"_posts/{date_str}-{clean_fn}.md"

        # SINGLE IMAGE AT THE TOP
        post_data = f"---\nlayout: post\ntitle: \"{new_title}\"\ncategory: {category}\n---\n\n![Headline]({news_img})\n\n{content}"

        os.makedirs("_posts", exist_ok=True) 
        with open(filename, "w") as f:
            f.write(post_data)
        print(f"--- SUCCESS: {category} Post (Bhogle Style) Created ---")

    except Exception as e:
        print(f"--- ERROR: {str(e)} ---")

if __name__ == "__main__":
    run()
