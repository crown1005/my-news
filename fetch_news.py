import requests
import feedparser
from datetime import datetime

# ---- 興味キーワード ----
KEYWORDS = ["AI", "機械学習", "セキュリティ", "データベース", "オラクル",
            "machine learning", "security", "database", "oracle"]

def filter_by_keywords(items):
    return [i for i in items if any(kw.lower() in i["title"].lower() for kw in KEYWORDS)]

# ---- Hacker News ----
def get_hn_stories(limit=30):  # 多めに取ってからフィルター
    ids = requests.get("https://hacker-news.firebaseio.com/v0/topstories.json").json()
    stories = []
    for id in ids[:limit]:
        item = requests.get(f"https://hacker-news.firebaseio.com/v0/item/{id}.json").json()
        stories.append({"title": item.get("title"), "url": item.get("url", f"https://news.ycombinator.com/item?id={id}")})
    return filter_by_keywords(stories)

# ---- はてブ ホットエントリ ----
def get_hatena_entries(limit=30):
    feed = feedparser.parse("https://b.hatena.ne.jp/hotentry.rss")
    items = [{"title": e.title, "url": e.link} for e in feed.entries[:limit]]
    return filter_by_keywords(items)

# ---- Reddit ----
SUBREDDITS = ["MachineLearning", "netsec", "database", "technology"]

def get_reddit_posts(limit=30):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    all_posts = []
    for sub in SUBREDDITS:
        try:
            res = requests.get(
                f"https://www.reddit.com/r/{sub}/top.json?limit={limit}&t=day",
                headers=headers,
                timeout=10
            )
            if res.status_code != 200:
                print(f"Reddit {sub}: ステータスコード {res.status_code} スキップします")
                continue
            posts = res.json()["data"]["children"]
            all_posts += [{"title": p["data"]["title"], "url": p["data"]["url"]} for p in posts]
        except Exception as e:
            print(f"Reddit {sub}: エラー {e} スキップします")
            continue
    return filter_by_keywords(all_posts)

    html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <title>My Newspaper - {date_str}</title>
  <style>
    body {{ font-family: sans-serif; max-width: 800px; margin: 40px auto; padding: 0 20px; }}
    h1 {{ border-bottom: 2px solid #333; }}
    li {{ margin: 8px 0; }}
    a {{ color: #333; text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}
  </style>
</head>
<body>
  <h1>📰 My Newspaper — {date_str}</h1>
  <p>🔍 キーワード：AI / 機械学習 / セキュリティ / データベース / オラクル</p>
  {section("🔥 Hacker News", hn, "#ff6600")}
  {section("⭐ はてブ ホットエントリ", hatena, "#008fde")}
  {section("🌍 Reddit", reddit, "#ff4500")}
</body>
</html>"""

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("index.html を生成しました")

if __name__ == "__main__":
    print("取得中...")
    hn = get_hn_stories()
    hatena = get_hatena_entries()
    reddit = get_reddit_posts()
    build_html(hn, hatena, reddit)
