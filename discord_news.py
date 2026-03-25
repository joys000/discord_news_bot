import feedparser
import requests
import json
import os
from datetime import datetime

# 1. 설정 (GitHub Actions의 env 설정과 이름을 맞췄습니다)
DISCORD_WEBHOOK_URL = os.environ.get('DISCORD_WEBHOOK') 
RSS_URL = "https://news.google.com/rss?hl=ko&gl=KR&ceid=KR:ko"
DB_FILE = "sent_links.txt"

# 키워드 및 색상 설정
KEYWORD_COLORS = {
    "급등": 15548997, "폭락": 2303786, "나스닥": 5763719, 
    "뉴욕증시": 5763719, "코스피": 3447003, "코스닥": 3447003, 
    "실적": 16776960, "연준": 10181046, "금리": 10181046, 
    "주식": 3447003, "증시": 3447003
}

def load_sent_links():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return set(line.strip() for line in f)
    return set()

def save_sent_link(link):
    with open(DB_FILE, "a", encoding="utf-8") as f:
        f.write(link + "\n")

def send_to_discord(entry, color):
    # ⚠️ 주소가 없으면 여기서 에러를 명확히 출력하게 만듦
    if not DISCORD_WEBHOOK_URL:
        print("❌ 에러: 웹훅 주소를 찾을 수 없습니다. GitHub Secrets를 확인하세요.")
        return

    payload = {
        "embeds": [{
            "title": entry.title,
            "url": entry.link,
            "description": f"📅 {entry.published}",
            "color": color,
            "footer": {"text": "실시간 주식 정보 서비스"}
        }]
    }
    requests.post(DISCORD_WEBHOOK_URL, json=payload)

def run_bot():
    print(f"🚀 [{datetime.now().strftime('%H:%M:%S')}] 스캔 시작...")
    
    # ⚠️ 주소 유무 사전 체크
    if not DISCORD_WEBHOOK_URL:
        print("❌ DISCORD_WEBHOOK 환경 변수가 설정되지 않았습니다.")
        return

    feed = feedparser.parse(RSS_URL)
    sent_links = load_sent_links()
    
    new_news_count = 0
    for entry in feed.entries[:30]:
        if entry.link not in sent_links:
            found_keyword = next((kw for kw in KEYWORD_COLORS if kw in entry.title), None)
            if found_keyword:
                send_to_discord(entry, KEYWORD_COLORS[found_keyword])
                save_sent_link(entry.link)
                new_news_count += 1
    
    print(f"🏁 작업 완료. 전송된 뉴스: {new_news_count}개")

if __name__ == "__main__":
    run_bot()
