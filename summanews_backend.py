# ✅ SummaNews 백엔드 main.py
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import feedparser
from summa.summarizer import summarize
import re

app = FastAPI()

# ✅ CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ RSS 주소 정의
LATEST_NEWS_RSS = "https://www.yna.co.kr/rss/news.xml"
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

# ✅ 기자명 및 언론사 제거 함수
def clean_news_content(text: str) -> str:
    text = re.sub(r'\([^)]*=\s*연합뉴스\)', '', text)  # (서울=연합뉴스) 형식 제거
    text = re.sub(r'[\w가-힣]{2,5}\s*기자[\s=:.·-]*', '', text)  # 기자명 제거
    text = re.sub(r'(연합뉴스|뉴스1|뉴시스|KBS|MBC|SBS|JTBC)[\s·:=-]*', '', text)  # 언론사 제거
    text = re.sub(r'\s+', ' ', text).strip()  # 공백 정리
    return text

# ✅ 요약 생성 함수
def get_summary(text: str) -> str:
    cleaned = clean_news_content(text)
    try:
        summary = summarize(cleaned, ratio=0.3)
        if not summary.strip():
            raise ValueError("요약 실패")
        return summary.strip()
    except:
        fallback = clean_news_content(text.strip().split('\n')[0])[:100]
        return "[원문 발췌] " + fallback + "..."

# ✅ 최신 뉴스 (5개)
@app.get("/api/news/latest")
async def get_latest_news(offset: int = Query(0)):
    feed = feedparser.parse(LATEST_NEWS_RSS)
    entries = feed.entries[offset:offset + 5]
    results = []

    for entry in entries:
        title = entry.title
        content = entry.get("description", "") or entry.get("summary", "")
        link = entry.link if 'link' in entry else "#"
        summary = get_summary(content)
        results.append({"category": "최신", "title": title, "summary": summary, "link": link})

    return {"news": results}

# ✅ 카테고리별 뉴스 (3개)
@app.get("/api/news/{category}")
async def get_news_by_category(category: str, offset: int = Query(0)):
    if category not in CATEGORY_RSS:
        return {"error": "카테고리를 찾을 수 없습니다."}

    feed = feedparser.parse(CATEGORY_RSS[category])
    entries = feed.entries[offset:offset + 3]
    results = []

    for entry in entries:
        title = entry.title
        content = entry.get("description", "") or entry.get("summary", "")
        link = entry.link if 'link' in entry else "#"
        summary = get_summary(content)
        results.append({"category": category, "title": title, "summary": summary, "link": link})

    return {"category": category, "news": results}
