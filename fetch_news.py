import requests
import feedparser
from datetime import datetime, timezone, timedelta

# ---- 興味キーワード ----
KEYWORDS = ["AI", "機械学習", "セキュリティ", "データベース", "オラクル",
            "machine learning", "security", "database", "oracle",
            "tech", "software", "python", "cloud", "cyber", "data",
            "テック", "技術", "エンジニア", "開発", "プログラム"]

def filter_by_keywords(items):
    return [i for i in items if any(kw.lower() in i["title"].lower() for kw in KEYWORDS)]

# ---- Hacker News ----
def get_hn_stories(limit=30):
    ids = requests.get("https://hacker-news.firebaseio.com/v0/topstories.json").json()
    stories = []
    for id in ids[:limit]:
        item = requests.get(f"https://hacker-news.firebaseio.com/v0/item/{id}.json").json()
        stories.append({"title": item.get("title"), "url": item.get("url", f"https://news.ycombinator.com/item?id={id}")})
    return stories

# ---- はてブ ホットエントリ ----
def get_hatena_entries(limit=30):
    feed = feedparser.parse("https://b.hatena.ne.jp/hotentry.rss")
    return [{"title": e.title, "url": e.link} for e in feed.entries[:limit]]

# ---- Reddit（RSS） ----
SUBREDDITS = ["MachineLearning", "netsec", "database", "technology"]

def get_reddit_posts():
    all_posts = []
    for sub in SUBREDDITS:
        try:
            feed = feedparser.parse(f"https://www.reddit.com/r/{sub}/top.rss?t=day")
            all_posts += [{"title": e.title, "url": e.link} for e in feed.entries]
        except Exception as e:
            print(f"Reddit {sub}: エラー {e} スキップします")
    return all_posts

# ---- RSSフィード一括取得 ----
RSS_FEEDS = {
    "TechCrunch":       "https://techcrunch.com/feed/",
    "Ars Technica":     "https://feeds.arstechnica.com/arstechnica/index",
    "The Hacker News":  "https://feeds.feedburner.com/TheHackersNews",
    "Zenn":             "https://zenn.dev/feed",
    "Qiita":            "https://qiita.com/popular-items/feed",
    "ITmedia":          "https://rss.itmedia.co.jp/rss/2.0/itmedia_all.xml",
}

def get_rss_articles(limit=30):
    all_items = {}
    for name, url in RSS_FEEDS.items():
        try:
            feed = feedparser.parse(url)
            all_items[name] = [{"title": e.title, "url": e.link} for e in feed.entries[:limit]]
            print(f"{name}: {len(all_items[name])}件")
        except Exception as e:
            print(f"{name}: エラー {e} スキップします")
            all_items[name] = []
    return all_items

# ---- HTML生成 ----
def build_section(title, items, color, icon):
    if not items:
        return f'<div class="section"><h2 style="color:{color}">{icon} {title}</h2><p class="empty">該当記事なし</p></div>'
    links = "\n".join(f'<li><a href="{i["url"]}" target="_blank">{i["title"]}</a></li>' for i in items)
    return f'<div class="section"><h2 style="color:{color}">{icon} {title}</h2><ul>{links}</ul></div>'

def build_html(hn, hatena, reddit, rss_articles):
    JST = timezone(timedelta(hours=9))
    date_str = datetime.now(JST).strftime("%Y年%m月%d日")

    sources = [
        ("Hacker News",  hn,      "#ff6600", "🔥"),
        ("はてブ",        hatena,  "#008fde", "⭐"),
        ("Reddit",       reddit,  "#ff4500", "🌍"),
    ]
    rss_meta = [
        ("TechCrunch",      "#e91e8c", "⚡"),
        ("Ars Technica",    "#2196f3", "🛡️"),
        ("The Hacker News", "#4caf50", "🔐"),
        ("Zenn",            "#9c27b0", "📝"),
        ("Qiita",           "#ff9800", "📌"),
        ("ITmedia",         "#00bcd4", "💻"),
    ]

    def render_tab_content(filtered):
        sections = ""
        for name, items, color, icon in sources:
            data = filter_by_keywords(items) if filtered else items
            sections += build_section(name, data, color, icon)
        for (name, color, icon), (_, items) in zip(rss_meta, rss_articles.items()):
            data = filter_by_keywords(items) if filtered else items
            sections += build_section(name, data, color, icon)
        return sections

    html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <title>My Newspaper - {date_str}</title>
  <style>
    * {{ box-sizing: border-box; }}
    body {{ font-family: sans-serif; max-width: 860px; margin: 40px auto; padding: 0 20px; background: #f9f9f9; }}
    h1 {{ border-bottom: 2px solid #333; padding-bottom: 8px; }}
    .keywords {{ background: #fff; padding: 8px 16px; border-radius: 8px; font-size: 0.9em; margin-bottom: 20px; border: 1px solid #ddd; }}
    .tabs {{ display: flex; gap: 8px; margin-bottom: 24px; }}
    .tab-btn {{
      padding: 10px 24px; border: none; border-radius: 8px 8px 0 0;
      cursor: pointer; font-size: 1em; font-weight: bold;
      background: #ddd; color: #555;
    }}
    .tab-btn.active {{ background: #333; color: #fff; }}
    .tab-content {{ display: none; }}
    .tab-content.active {{ display: block; }}
    .section {{ background: #fff; border-radius: 8px; padding: 16px 24px; margin-bottom: 20px; border: 1px solid #eee; }}
    h2 {{ margin-top: 0; font-size: 1.1em; }}
    li {{ margin: 8px 0; line-height: 1.5; }}
    a {{ color: #333; text-decoration: none; }}
    a:hover {{ text-decoration: underline; color: #0066cc; }}
    .empty {{ color: #999; font-size: 0.9em; }}
  </style>
</head>
<body>
  <h1>📰 My Newspaper — {date_str}</h1>
  <p class="keywords">🔍 フィルターキーワード：AI / 機械学習 / セキュリティ / データベース / オラクル / tech / software / python / cloud / cyber / data</p>

  <div class="tabs">
    <button class="tab-btn active" onclick="switchTab('filtered')">🎯 キーワードあり</button>
    <button class="tab-btn" onclick="switchTab('all')">📋 全記事</button>
  </div>

  <div id="filtered" class="tab-content active">
    {render_tab_content(filtered=True)}
  </div>
  <div id="all" class="tab-content">
    {render_tab_content(filtered=False)}
  </div>

  <script>
    function switchTab(name) {{
      document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
      document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));
      document.getElementById(name).classList.add('active');
      event.target.classList.add('active');
    }}
  </script>
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
    rss_articles = get_rss_articles()
    build_html(hn, hatena, reddit, rss_articles)
