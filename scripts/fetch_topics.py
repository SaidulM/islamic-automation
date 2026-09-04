"""
প্রতিদিন কয়েকবার চলে (cron) — YouTube-এ ট্রেন্ডিং ইসলামিক শর্ট ভিডিওর
টাইটেল দেখে, LLM দিয়ে নতুন ইউনিক টপিক আইডিয়া বানিয়ে Sheet-এর Pool-এ জমা করে।
লক্ষ্য: প্রতিদিন ~৫০টা, যাতে সবসময় অন্তত ১০ দিনের বাফার (~৫০০টা) থাকে।
"""
import os
import requests

from scripts import sheet_client, llm_client

YOUTUBE_API_KEY = os.environ["YOUTUBE_API_KEY"]

SEED_KEYWORDS = [
    "islamic shorts hindi",
    "quran story shorts",
    "hadith motivation shorts",
    "islamic cartoon story",
    "prophet stories hindi",
]

DAILY_TARGET = 50
BUFFER_DAYS = 10


def fetch_trending_titles():
    titles = []
    for kw in SEED_KEYWORDS:
        resp = requests.get(
            "https://www.googleapis.com/youtube/v3/search",
            params={
                "part": "snippet",
                "q": kw,
                "type": "video",
                "order": "viewCount",
                "maxResults": 10,
                "key": YOUTUBE_API_KEY,
            },
            timeout=20,
        )
        resp.raise_for_status()
        for item in resp.json().get("items", []):
            titles.append(item["snippet"]["title"])
    return titles


def main():
    current_pool = sheet_client.pool_count()
    buffer_target = DAILY_TARGET * BUFFER_DAYS

    if current_pool >= buffer_target:
        sheet_client.log("Fetch_Topics", f"Pool already full ({current_pool}) — স্কিপ করা হলো")
        return

    titles = fetch_trending_titles()
    new_topics = llm_client.suggest_topics(titles, n=DAILY_TARGET)
    sheet_client.save_pool_topics(new_topics)
    sheet_client.log("Fetch_Topics", f"{len(new_topics)}টা নতুন টপিক জমা হলো (pool ছিল {current_pool})")


if __name__ == "__main__":
    main()
