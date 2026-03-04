import os
from groq import Groq
from config import NEUTRALITY_RULES

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def process_news_item(news_item):
    """Process a single news item through AI for neutral summarization"""
    
    prompt = f"""
Title: {news_item['title']}
Source: {news_item['source']}
Content: {news_item['summary']}
Link: {news_item['link']}

Task: Create a neutral, factual news post for a Telegram channel.

Format your response EXACTLY like this:
📌 [One sentence factual headline]

📋 FACTS:
• [Fact 1]
• [Fact 2]  
• [Fact 3]

🔗 Source: [Source name] | [link]

#WorldNews #[relevant tag]
"""

    try:
        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {"role": "system", "content": NEUTRALITY_RULES},
                {"role": "user", "content": prompt}
            ],
            max_tokens=400,
            temperature=0.3
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        print(f"AI processing error: {e}")
        return None

def find_common_facts(news_items):
    """Find news stories covered by multiple sources - more reliable"""
    
    prompt = f"""
Here are news headlines from multiple global sources:

{chr(10).join([f"- [{item['source']}]: {item['title']}" for item in news_items[:20]])}

Task: Identify the TOP 3 most important stories that appear across MULTIPLE sources.
For each story, list which sources covered it.

Format:
STORY 1: [topic]
Sources: [source1, source2, source3]

STORY 2: [topic]  
Sources: [source1, source2]

STORY 3: [topic]
Sources: [source1, source2, source3]
"""

    try:
        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {"role": "system", "content": "You are a neutral news analyst. Be concise and factual."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300,
            temperature=0.2
        )
        return response.choices[0].message.content
        
    except Exception as e:
        print(f"Error finding common facts: {e}")
        return None
