import schedule, time, asyncio, json, os, hashlib
from news_fetcher import get_all_news, group_similar_news
from ai_processor import analyze_story_group, process_news_item
from publisher import publish_to_channel
from config import POST_INTERVAL_MINUTES

POSTED_FILE = "posted_news.json"

def load_posted():
    if os.path.exists(POSTED_FILE):
        try:
            with open(POSTED_FILE, "r") as f:
                return set(json.load(f))
        except:
            return set()
    return set()

def save_posted(posted):
    with open(POSTED_FILE, "w") as f:
        json.dump(list(posted)[-500:], f)

def make_hash(title):
    return hashlib.md5(title.lower().strip().encode()).hexdigest()

def filter_new_news(all_news, posted):
    return [item for item in all_news if make_hash(item['title']) not in posted]

def pick_image(news_group):
    for item in news_group:
        if item.get('image'):
            return item['image']
    return None

async def run_news_cycle():
    print("Starting news cycle...")
    posted = load_posted()
    print("Already posted: " + str(len(posted)) + " stories")
    print("Fetching news from all sources...")
    all_news = get_all_news()
    if not all_news:
        print("No news fetched!")
        return
    print("Fetched: " + str(len(all_news)) + " items total")
    new_news = filter_new_news(all_news, posted)
    print("New (not posted yet): " + str(len(new_news)) + " items")
    if not new_news:
        print("No new news to post!")
        return
    print("Grouping stories from multiple sources...")
    story_groups = group_similar_news(new_news)
    print("Found " + str(len(story_groups)) + " cross-source stories")
    published_count = 0
    if story_groups:
        for group in story_groups[:3]:
            print("Analyzing story by " + str(len(group)) + " sources: " + group[0]['title'][:50])
            analyzed = analyze_story_group(group)
            if analyzed:
                image = pick_image(group)
                await publish_to_channel(analyzed, image_url=image)
                for item in group:
                    posted.add(make_hash(item['title']))
                published_count += 1
                await asyncio.sleep(10)
    else:
        print("No cross-source stories, posting individual news...")
        for news_item in new_news[:3]:
            print("Processing: " + news_item['title'][:50])
            processed = process_news_item(news_item)
            if processed:
                image = news_item.get('image')
                await publish_to_channel(processed, image_url=image)
                posted.add(make_hash(news_item['title']))
                published_count += 1
                await asyncio.sleep(5)
    save_posted(posted)
    print("Cycle complete! Published: " + str(published_count) + " posts")

def scheduled_job():
    asyncio.run(run_news_cycle())

def main():
    print("WorldAiNews Bot Starting...")
    print("Posting every " + str(POST_INTERVAL_MINUTES) + " minutes")
    scheduled_job()
    schedule.every(POST_INTERVAL_MINUTES).minutes.do(scheduled_job)
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    main()