import re, json
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup

BASE = "https://www.rimnow.net/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; RimSatireBot/1.0; +https://fallinn2000.github.io/dailoul-news-for-git/)"
}

def normalize(text):
    t = re.sub(r"\s+", " ", text or "").strip()
    t = re.sub(r"[^\w\u0600-\u06FF ]+", "", t)
    return t

def fetch_home():
    r = requests.get(BASE, headers=HEADERS, timeout=20)
    r.raise_for_status()
    return r.text

def parse_titles(html):
    soup = BeautifulSoup(html, "lxml")
    links = []
    for a in soup.select("a"):
        txt = a.get_text(strip=True)
        href = a.get("href")
        if not txt or not href:
            continue
        if len(txt) < 12 or href.startswith("#"):
            continue
        links.append((normalize(txt), urljoin(BASE, href)))
    return links

def top_topics(links, k=5):
    counts, first_url = {}, {}
    for title, url in links:
        counts[title] = counts.get(title, 0) + 1
        if title not in first_url:
            first_url[title] = url
    ranked = sorted(counts.items(), key=lambda x: (-x[1], x[0]))[:k]
    return [{"title": t, "url": first_url[t], "count": c} for t, c in ranked]

if __name__ == "__main__":
    html = fetch_home()
    links = parse_titles(html)
    items = top_topics(links, k=5)
    print(json.dumps({"items": items}, ensure_ascii=False))
