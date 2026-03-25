import feedparser
import requests
import json
import os
from datetime import datetime

# 1. 설정
RSS_URL = "https://news.google.com/rss?hl=ko&gl=KR&ceid=KR:ko"
DISCORD_WEBHOOK_URL = "여기에_디스코드_웹훅_주소를_넣으세요"
DB_FILE = "sent_links.txt"

# 2. 키워드별 색상 매핑 (10진수 색상 코드 사용)
# 색상 참고: https://gist.github.com/thomasbnt/b6f455e2c7d744b2636933db59c9d427
KEYWORD_COLORS = {
    "급등": 15548997,   # 빨강 (심각/강조)
    "폭락": 2303786,    # 어두운 파랑
    "나스닥": 5763719,  # 녹색
    "뉴욕증시": 5763719,
    "코스피": 3447003,   # 파랑
    "코스닥": 3447003,
    "실적": 16776960,   # 노랑/골드
    "연준": 10181046,   # 보라
    "금리": 10181046,
    "주식": 3447003,    # 기본 파랑
    "증시": 3447003
}
DEFAULT_COLOR = 9807270 # 회색 (기본값)

def load_sent_links():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return set(line.strip() for line in f)
    return set()

def save_sent_link(link):
    with open(DB_FILE, "a", encoding="utf-8") as f:
        f.write(link + "\n")

def send_to_discord(entry, color):
    """임베드 색상을 적용하여 전송"""
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
    print(f"🚀 [{datetime.now().strftime('%H:%M:%S')}] 필터링 스캔 시작...")
    feed = feedparser.parse(RSS_URL)
    sent_links = load_sent_links()
    
    new_news_count = 0
    for entry in feed.entries[:30]:
        if entry.link not in sent_links:
            # 🔍 키워드 검사 및 색상 결정
            found_keyword = None
            for kw in KEYWORD_COLORS.keys():
                if kw in entry.title:
                    found_keyword = kw
                    break # 첫 번째 발견된 키워드에서 멈춤
            
            if found_keyword:
                target_color = KEYWORD_COLORS[found_keyword]
                send_to_discord(entry, target_color)
                save_sent_link(entry.link)
                new_news_count += 1
                print(f"🎯 발견({found_keyword}): {entry.title[:20]}...")

    print(f"🏁 뉴스 {new_news_count}개 전송 완료.")

if __name__ == "__main__":
    run_bot()