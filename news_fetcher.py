import feedparser, requests, socket
from config import RSS_FEEDS, NEWS_API_KEY
from difflib import SequenceMatcher
socket.setdefaulttimeout(5)
def fetch_rss_news():
    r=[]
    for u in RSS_FEEDS:
        try:
            f=feedparser.parse(u)
            s=f.feed.get('title',u)
            for e in f.entries[:3]:
                r.append({'title':e.get('title',''),'summary':e.get('summary',e.get('description','')),'link':e.get('link',''),'source':s,'published':e.get('published','')})
        except Exception as ex:
            print("skip:"+str(ex))
    return r
def fetch_newsapi_headlines():
    if not NEWS_API_KEY:return[]
    try:
        d=requests.get("https://newsapi.org/v2/top-headlines?language=en&pageSize=10&apiKey="+NEWS_API_KEY,timeout=5).json()
        return[{'title':a.get('title',''),'summary':a.get('description',''),'link':a.get('url',''),'source':a.get('source',{}).get('name','NewsAPI'),'published':a.get('publishedAt','')}for a in d.get('articles',[])]
    except Exception as ex:
        print("api:"+str(ex));return[]
def similar(a,b):return SequenceMatcher(None,a.lower(),b.lower()).ratio()
def extract_keywords(t):
    sw={'the','a','an','in','on','at','to','for','of','and','or','but','is','are','was','were','be','been','has','have','had','will','would','could','should','may','might','as','by','from','with','about','into','after','before','during','says','said','say'}
    return set(t.lower().split())-sw
def group_similar_news(all_news,similarity_threshold=0.3,min_sources=2):
    groups=[];used=set()
    for i,item in enumerate(all_news):
        if i in used:continue
        g=[item];ki=extract_keywords(item['title'])
        for j,o in enumerate(all_news):
            if j<=i or j in used or item['source']==o['source']:continue
            kj=extract_keywords(o['title'])
            ov=len(ki&kj)/min(len(ki),len(kj)) if ki and kj else 0
            if ov>=similarity_threshold or similar(item['title'],o['title'])>=0.4:
                g.append(o);used.add(j)
        if len(g)>=min_sources:groups.append(g);used.add(i)
    groups.sort(key=lambda g:len(g),reverse=True)
    return groups
def get_all_news():return fetch_rss_news()+fetch_newsapi_headlines()