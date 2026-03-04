import os
from groq import Groq
from config import NEUTRALITY_RULES

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def analyze_story_group(news_group):
    """Analyze a group of news items covering the same story from different sources"""
    
    sources_text = "\n".join([
        f"📰 {item['source']}: \"{item['title']}\"
   {item['summary'][:200] if item['summary'] else ''}\n   🔗 {item['link']}"
        for item in news_group
    ])
    
    source_names = ", ".join([item['source'] for item in news_group])
    
    prompt = f"""
You are analyzing the SAME news story as reported by {len(news_group)} different media sources.

Here are the reports:

{sources_text}

Your task: Create an independent, neutral Telegram post that:
1. Identifies the CORE FACTS confirmed by ALL sources
2. Notes HOW EACH SOURCE frames the story differently
3. Provides an INDEPENDENT CONCLUSION based on all perspectives

Format your response EXACTLY like this:

🌍 <b>ТЕМА: [One line topic in Russian]</b>
📊 Покрыто источниками: {len(news_group)} ({source_names})

{chr(10).join([f"📰 {item['source']}: [one sentence summary]" for item in news_group])}

✅ <b>ПОДТВЕРЖДЕНО ВСЕМИ:</b>
• [Confirmed fact 1]
• [Confirmed fact 2]

🔍 <b>РАЗЛИЧИЯ В ПОДАЧЕ:</b>
• [How sources differ in framing]

🧠 <b>НЕЗАВИСИМЫЙ ВЫВОД:</b>
[2-3 sentences neutral conclusion]

🔗 Источники: {" | ".join([item['link'] for item in news_group[:3]])}

#WorldNews #[relevant tag]
"""
    
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": NEUTRALITY_RULES},
                {"role": "user", "content": prompt}
            ],
            max_tokens=600,
            temperature=0.3
        )
        return response.choices[0].message.content
        
    except Exception as e:
        print(f"AI processing error: {e}")
        return None

def process_news_item(news_item):
    """Fallback: Process a single news item"""
    
    prompt = f"""
Title: {news_item['title']}
Source: {news_item['source']}
Content: {news_item['summary']}
Link: {news_item['link']}

Create a neutral, factual news post for a Telegram channel in this format:

📌 [One sentence factual headline]

📋 FACTS:
• [Fact 1]
• [Fact 2]
• [Fact 3]

🔗 Source: {news_item['source']} | {news_item['link']}

#WorldNews #[relevant tag]
"""
    
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
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
