import schedule
import time
import asyncio
from news_fetcher import get_all_news
from ai_processor import process_news_item, find_common_facts
from publisher import publish_to_channel, publish_daily_summary
from config import POST_INTERVAL_MINUTES
import random

async def run_news_cycle():
    """Main news cycle: fetch → process → publish"""
    print("🔄 Starting news cycle...")
    
    # Step 1: Fetch news from all sources
    print("📰 Fetching news from all sources...")
    all_news = get_all_news()
    
    if not all_news:
        print("❌ No news fetched!")
        return
    
    print(f"✅ Fetched {len(all_news)} news items from {len(set(item['source'] for item in all_news))} sources")
    
    # Step 2: Find stories covered by multiple sources (more reliable)
    print("🔍 Finding cross-source stories...")
    common_facts = find_common_facts(all_news)
    
    if common_facts:
        summary_message = f"🌍 <b>TOP STORIES — Multiple Sources Confirm:</b>\n\n{common_facts}"
        await publish_to_channel(summary_message)
        await asyncio.sleep(3)
    
    # Step 3: Pick 2-3 random news items and process them individually
    selected_news = random.sample(all_news, min(3, len(all_news)))
    
    for news_item in selected_news:
        print(f"🧠 Processing: {news_item['title'][:50]}...")
        processed = process_news_item(news_item)
        
        if processed:
            await publish_to_channel(processed)
            await asyncio.sleep(5)  # Delay between posts
    
    print("✅ News cycle complete!")

def scheduled_job():
    """Run the async news cycle"""
    asyncio.run(run_news_cycle())

def main():
    print("🚀 WorldAiNews Bot Starting...")
    print(f"⏰ Posting every {POST_INTERVAL_MINUTES} minutes")
    
    # Run immediately on start
    scheduled_job()
    
    # Schedule regular runs
    schedule.every(POST_INTERVAL_MINUTES).minutes.do(scheduled_job)
    
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    main()
