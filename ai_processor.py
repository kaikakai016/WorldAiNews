import os
from groq import Groq
from config import NEUTRALITY_RULES

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def analyze_story_group(news_group):
    """Analyze a group of news items covering the same story from different sources"""
    
    sources_lines = []
    for item in news_group:
        source = item['source']
        title = item['title']
        summary = item['summary'][:200] if item['summary'] else ''
        link = item['link']
        sources_lines.append("Source: " + source + "\nTitle: " + title + "\nSummary: " + summary + "\nLink: " + link + "\n")
    
    sources_text = "\n".join(sources_lines)
    source_names = ", ".join([item['source'] for item in news_group])
    source_links = " | ".join([item['link'] for item in news_group[:3]])
    count = len(news_group)

    prompt = (
        "You are analyzing the SAME news story as reported by " + str(count) + " different media sources.\n\n"
        "Here are the reports:\n\n" + sources_text + "\n\n"
        "Your task: Create an independent, neutral Telegram post that:\n"
        "1. Identifies the CORE FACTS confirmed by ALL sources\n"
        "2. Notes HOW EACH SOURCE frames the story differently\n"
        "3. Provides an INDEPENDENT CONCLUSION based on all perspectives\n\n"
        "Format your response EXACTLY like this:\n\n"
        "🌍 ТЕМА: [One line topic in Russian]\n"
        "📊 Покрыто источниками: " + str(count) + " (" + source_names + ")\n\n"
        "[For each source write: 📰 SourceName: one sentence summary]\n\n"
        "✅ ПОДТВЕРЖДЕНО ВСЕМИ:\n"
        "• [Confirmed fact 1]\n"
        "• [Confirmed fact 2]\n\n"
        "🔍 РАЗЛИЧИЯ В ПОДАЧЕ:\n"
        "• [How sources differ in framing]\n\n"
        "🧠 НЕЗАВИСИМЫЙ ВЫВОД:\n"
        "[2-3 sentences neutral conclusion]\n\n"
        "🔗 Источники: " + source_links + "\n\n"
        "#WorldNews #[relevant tag]"
    )
    
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
        print("AI processing error: " + str(e))
        return None

def process_news_item(news_item):
    """Fallback: Process a single news item"""
    
    title = news_item['title']
    source = news_item['source']
    summary = news_item['summary']
    link = news_item['link']

    prompt = (
        "Title: " + title + "\n"
        "Source: " + source + "\n"
        "Content: " + summary + "\n"
        "Link: " + link + "\n\n"
        "Create a neutral, factual news post for a Telegram channel in this format:\n\n"
        "📌 [One sentence factual headline]\n\n"
        "📋 FACTS:\n"
        "• [Fact 1]\n"
        "• [Fact 2]\n"
        "• [Fact 3]\n\n"
        "🔗 Source: " + source + " | " + link + "\n\n"
        "#WorldNews #[relevant tag]"
    )
    
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
        print("AI processing error: " + str(e))
        return None