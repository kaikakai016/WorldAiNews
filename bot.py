import schedule
import time
import asyncio
from news_fetcher import get_all_news, group_similar_news
from ai_processor import analyze_story_group, process_news_item
from publisher import publish_to_channel
from config import POST_INTERVAL_MINUTES

async def run_news_cycle():
    """Main news cycle: fetch → group → analyze → publish"""
    print("🔄 Starting news cycle...")
    
    # Step 1: Fetch news from all sources
    print("📰 Fetching news from all sources...")
    all_news = get_all_news()
    
    if not all_news:
        print("❌ No news fetched!")
        return
    
    print(f"✅ Fetched {len(all_news)} news items from {len(set(item['source'] for item in all_news))} sources")
    
    # Step 2: Group similar stories from different sources
    print("🔍 Grouping stories from multiple sources...")
    story_groups = group_similar_news(all_news)
    print(f"📦 Found {len(story_groups)} cross-source stories")
    
    if story_groups:
        # Post top 3 most covered stories
        for group in story_groups[:3]:
            print(f"🧠 Analyzing story covered by {len(group)} sources: {group[0]['title'][:50]}...")
            analyzed = analyze_story_group(group)
            
            if analyzed:
                await publish_to_channel(analyzed)
                await asyncio.sleep(10)  # Delay between posts
    else:
        # Fallback: post individual news if no groups found
        print("⚠️ No cross-source stories found, posting individual news...")
        for news_item in all_news[:3]:
            print(f"🧠 Processing: {news_item['title'][:50]}...")
            processed = process_news_item(news_item)
            if processed:
                await publish_to_channel(processed)
                await asyncio.sleep(5)
    
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