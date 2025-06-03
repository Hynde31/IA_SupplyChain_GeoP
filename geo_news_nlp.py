import feedparser
import spacy
import streamlit as st
from collections import defaultdict
import re
from datetime import datetime
import subprocess

# Téléchargement automatique des modèles spaCy si besoin
def download_model(model_name):
    try:
        spacy.load(model_name)
    except OSError:
        subprocess.run(["python", "-m", "spacy", "download", model_name], check=True)

download_model("fr_core_news_sm")
download_model("en_core_web_sm")

@st.cache_resource
def get_nlp():
    try:
        return spacy.load("fr_core_news_sm")
    except:
        return spacy.load("en_core_web_sm")

nlp = get_nlp()

KEYWORDS = {
    "grève": 2, "strike": 2, "embargo": 3, "blocus": 3, "blockade": 3,
    "conflit": 2, "conflict": 2, "guerre": 3, "war": 3, "manifestation": 1,
    "protest": 1, "retard": 1, "delay": 1, "tension": 2, "attaque": 3,
    "attack": 3, "sanction": 2, "tariff": 2, "douane": 2, "customs": 2,
}

QUICK_COORDS = {
    "Casablanca": (33.5731, -7.5898), "Maroc": (31.7917, -7.0926),
    "France": (46.6034, 1.8883), "USA": (39.8283, -98.5795),
    "Toulouse": (43.6047, 1.4442), "Shanghai": (31.2304, 121.4737),
    "Ukraine": (48.3794, 31.1656), "Chine": (35.8617, 104.1954),
    "China": (35.8617, 104.1954), "Russia": (61.5240, 105.3188),
    "Russie": (61.5240, 105.3188), "Allemagne": (51.1657, 10.4515),
    "Germany": (51.1657, 10.4515), "Wichita": (37.6872, -97.3301),
    "Rochefort": (45.9420, -0.9627)
}

RSS_FEEDS = [
    "http://feeds.reuters.com/reuters/worldNews",
    "https://www.lemonde.fr/international/rss_full.xml"
]

@st.cache_data(ttl=3600)
def fetch_feed(feed_url):
    return feedparser.parse(feed_url)

def get_news_for_period(period_yyyymm, max_news_per_feed=5):
    period_dt = datetime.strptime(period_yyyymm, "%Y-%m")
    filtered_news = []
    for feed_url in RSS_FEEDS:
        feed = fetch_feed(feed_url)
        for entry in feed.entries[:max_news_per_feed]:
            try:
                if hasattr(entry, "published_parsed") and entry.published_parsed:
                    pub_date = datetime(*entry.published_parsed[:6])
                elif hasattr(entry, "updated_parsed") and entry.updated_parsed:
                    pub_date = datetime(*entry.updated_parsed[:6])
                else:
                    pub_date = period_dt
                if pub_date.year == period_dt.year and pub_date.month == period_dt.month:
                    filtered_news.append({
                        "title": entry.title,
                        "summary": getattr(entry, "summary", ""),
                        "date": pub_date.strftime("%Y-%m-%d")
                    })
            except Exception:
                continue
    return filtered_news

def extract_geo_and_impact(news_items):
    impact_dict = defaultdict(lambda: {"impact": 0, "lat": None, "lon": None, "news": []})
    for news in news_items:
        txt = (news["title"] + " " + news["summary"]).replace('&quot;', '"')
        doc = nlp(txt)
        geo_names = [ent.text for ent in doc.ents if ent.label_ in ("LOC", "GPE")]
        impact_score = 0
        for word, score in KEYWORDS.items():
            if re.search(rf"\b{re.escape(word)}\b", txt, re.IGNORECASE):
                impact_score = max(impact_score, score)
        for geo in set(geo_names):
            coords = QUICK_COORDS.get(geo)
            if coords:
                lat, lon = coords
                impact_dict[geo]["impact"] = max(impact_dict[geo]["impact"], impact_score)
                impact_dict[geo]["lat"] = lat
                impact_dict[geo]["lon"] = lon
                impact_dict[geo]["news"].append(news)
    impacts = []
    for geo, info in impact_dict.items():
        if info["impact"] > 0 and info["lat"] and info["lon"]:
            impacts.append({"zone": geo, "lat": info["lat"], "lon": info["lon"], "impact": info["impact"]})
    return impacts

def get_news_impact_for_month(month_str):
    news = get_news_for_period(month_str)
    impacts = extract_geo_and_impact(news)
    return news, impacts

if __name__ == "__main__":
    month = "2025-05"
    news, impacts = get_news_impact_for_month(month)
    print("News trouvées :", news)
    print("Impacts géopolitiques détectés :", impacts)
