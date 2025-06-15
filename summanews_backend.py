from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import feedparser
from summa.summarizer import summarize

app = FastAPI()

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ 최신 뉴스 RSS (변경됨)
LATEST_NEWS_RSS = "https://www.yna.co.kr/rss/news.xml"

# ✅ 카테고리별 RSS
CATEGORY_RSS = {
    "정치": "https://rss.donga.com/politics.xml",
    "연예": "https://www.yna.co.kr/rss/entertainment.xml",
    "생활-문화": "https://news.sbs.co.kr/news/SectionRssFeed.do?sectionId=08&plink=RSSREADER",
    "경제": "https://rss.donga.com/economy.xml",
    "건강": "https://www.yna.co.kr/rss/health.xml",
    "세계": "https://rss.donga.com/international.xml",
    "스포츠": "https://rss.donga.com/sports.xml",
    "환경": "https://api.newswire.co.kr/rss/industry/1500"
}

# ✅ 최신 뉴스 (5개씩)
@app.get("/api/news/latest")
async def get_latest_news(offset: int = Query(0)):
    feed = feedparser.parse(LATEST_NEWS_RSS)
    entries = feed.entries[offset:offset+5]
    results = []

    if not entries:
        return {"news": [], "message": "❗ 더 이상 가져올 뉴스가 없습니다."}

    for entry in entries:
        title = entry.title
        content = entry.get("description", "") or entry.get("summary", "")
        link = entry.link if 'link' in entry else "#"

        try:
            summary = summarize(content, ratio=0.3)
            if not summary.strip():
                raise ValueError("Empty summary")
        except:
            summary = "[원문 발췌] " + content.strip().split('\n')[0][:100] + "..."

        results.append({
            "category": "최신",
            "title": title,
            "summary": summary,
            "link": link
        })

    return {"news": results}

# ✅ 카테고리별 뉴스 (3개씩)
@app.get("/api/news/{category}")
async def get_news_by_category(category: str, offset: int = Query(0)):
    if category not in CATEGORY_RSS:
        return {"error": "카테고리를 찾을 수 없습니다."}

    feed = feedparser.parse(CATEGORY_RSS[category])
    entries = feed.entries[offset:offset+3]
    results = []

    if not entries:
        return {"news": [], "message": "❗ 더 이상 가져올 뉴스가 없습니다."}

    for entry in entries:
        title = entry.title
        content = entry.get("description", "") or entry.get("summary", "")
        link = entry.link if 'link' in entry else "#"

        try:
            summary = summarize(content, ratio=0.3)
            if not summary.strip():
                raise ValueError("Empty summary")
        except:
            summary = "[원문 발췌] " + content.strip().split('\n')[0][:100] + "..."

        results.append({
            "category": category,
            "title": title,
            "summary": summary,
            "link": link
        })

    return {"category": category, "news": results}
