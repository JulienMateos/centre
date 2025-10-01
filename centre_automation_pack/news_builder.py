#!/usr/bin/env python3
import feedparser, os, json, datetime as dt
from bs4 import BeautifulSoup

# Configurable RSS sources (edit if you like)
RSS_WORLD = [
    "https://www.reuters.com/world/rss",           # World
    "https://www.reuters.com/markets/rss",         # Markets
    "https://feeds.a.dj.com/rss/RSSWorldNews.xml", # WSJ World (headlines only)
]
RSS_TECH = [
    "https://www.reuters.com/technology/rss",
    "https://feeds.arstechnica.com/arstechnica/index",
]

MAX_ITEMS_PER_SECTION = 3

def clean(text):
    if not text: return ""
    # strip HTML if any
    soup = BeautifulSoup(text, "html.parser")
    return " ".join(soup.get_text().split())

def summarize_entries(entries, n):
    out = []
    for e in entries[:n]:
        title = clean(getattr(e, "title", ""))
        summary = clean(getattr(e, "summary", ""))
        if not summary:
            summary = ""
        out.append({"title": title, "text": summary[:220]+"..." if len(summary) > 220 else summary})
    return out

def collect():
    world_entries = []
    for url in RSS_WORLD:
        try:
            feed = feedparser.parse(url)
            world_entries.extend(feed.entries[:5])
        except Exception:
            pass

    tech_entries = []
    for url in RSS_TECH:
        try:
            feed = feedparser.parse(url)
            tech_entries.extend(feed.entries[:5])
        except Exception:
            pass

    # Sort by published date if available
    def pubdate(e):
        try:
            return dt.datetime(*e.published_parsed[:6])
        except Exception:
            return dt.datetime.utcnow()
    world_entries.sort(key=pubdate, reverse=True)
    tech_entries.sort(key=pubdate, reverse=True)

    fr_sections = [
        {"title": "Monde", "text": " • ".join([clean(getattr(e, "title", "")) for e in world_entries[:MAX_ITEMS_PER_SECTION]])},
        {"title": "Business", "text": "Principales tendances marchés & entreprises (sélection)."},
        {"title": "Tech", "text": " • ".join([clean(getattr(e, "title", "")) for e in tech_entries[:MAX_ITEMS_PER_SECTION]])},
    ]
    en_sections = [
        {"title": "World", "text": " • ".join([clean(getattr(e, "title", "")) for e in world_entries[:MAX_ITEMS_PER_SECTION]])},
        {"title": "Business", "text": "Top market & corporate trends (curated)."},
        {"title": "Tech", "text": " • ".join([clean(getattr(e, "title", "")) for e in tech_entries[:MAX_ITEMS_PER_SECTION]])},
    ]

    data = {
        "fr": { "sections": fr_sections },
        "en": { "sections": en_sections },
        "kpi": ["Headlines: {} world / {} tech".format(min(len(world_entries), MAX_ITEMS_PER_SECTION),
                                                       min(len(tech_entries), MAX_ITEMS_PER_SECTION))],
        "story": "Pourquoi ça compte / Why it matters: Focus on macro moves, policy shifts, and signals for decision‑making."
    }
    return data

def main():
    path = os.path.join("data", "news.json")
    os.makedirs("data", exist_ok=True)
    data = collect()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Wrote {path}")

if __name__ == "__main__":
    main()
