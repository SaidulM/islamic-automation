import os
import requests
import json
import re

# পরিবেশ ভেরিয়েবল
TG_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')
COMMAND = os.getenv('COMMAND', '').lower()

def send_tg(text):
    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"}
    requests.post(url, json=payload)

def get_topics():
    # পদ্ধতি ১: সরাসরি ইউটিউব সার্চ পেজ থেকে তথ্য সংগ্রহের চেষ্টা
    search_query = "islamic+facts+mystery+history+bangla"
    url = f"https://www.youtube.com/results?search_query={search_query}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        # ভিডিও টাইটেল খোঁজার আরও উন্নত পদ্ধতি
        titles = re.findall(r'"title":\{"runs":\[\{"text":"(.*?)"\}\]', response.text)
        
        # কিছু কমন শব্দ ফিল্টার করা যাতে ভালো টপিক পাওয়া যায়
        filtered_topics = []
        for t in titles:
            t_clean = t.encode('utf-16', 'surrogatepass').decode('utf-16') # ইমোজি হ্যান্ডলিং
            if any(word in t_clean.lower() for word in ['islam', 'mysterious', 'history', 'allah', 'prophet', 'facts']):
                if len(t_clean) > 30 and t_clean not in filtered_topics:
                    filtered_topics.append(t_clean)
            if len(filtered_topics) >= 3:
                break
        
        if filtered_topics:
            return filtered_topics
            
    except Exception as e:
        print(f"Scraping error: {e}")

    # পদ্ধতি ২: যদি উপরের পদ্ধতি কাজ না করে তবে স্ট্যাটিক ট্রেন্ডিং টপিক (ফেইলসেফ)
    return [
        "পৃথিবীর রহস্যময় ৫টি ইসলামিক স্থান যা আপনাকে অবাক করবে",
        "ইতিহাসের পাতায় হারানো এক মহান মুসলিম বীরের কাহিনী",
        "বিজ্ঞান ও ইসলামের অলৌকিক কিছু তথ্য যা জানা প্রয়োজন"
    ]

def main():
    if not TG_TOKEN or not CHAT_ID:
        print("Missing Telegram Credentials")
        return

    if COMMAND == "/start":
        send_tg("<b>আসসালামু আলাইকুম!</b>\nআমি আপনার জন্য ভাইরাল ইসলামিক টপিক খুঁজছি। একটু সময় দিন...")
        
        topics = get_topics()
        
        message = "🔍 <b>আমি আজ এই ৩টি ভাইরাল টপিক খুঁজে পেয়েছি:</b>\n\n"
        for i, topic in enumerate(topics, 1):
            message += f"<b>{i}.</b> {topic}\n"
        
        message += "\nআপনি কোনটি নিয়ে কাজ করতে চান? (১, ২ বা ৩ লিখে আমাকে রিপ্লাই দিন)"
        send_tg(message)

    elif COMMAND in ["1", "2", "3"]:
        # এখানে পরে Qwen মডেলের স্ক্রিপ্ট জেনারেশন যোগ হবে
        topic_idx = int(COMMAND) - 1
        send_tg(f"✅ আপনি <b>টপিক {COMMAND}</b> পছন্দ করেছেন।\nআমি এখন এটি নিয়ে চমৎকার একটি স্ক্রিপ্ট লিখছি। (Qwen Model loading...)")
        
        # পরবর্তী ধাপের জন্য সেভ করার মেসেজ (টেস্ট)
        send_tg("<i>স্ক্রিপ্ট তৈরির কাজ চলছে, এটি শেষ হলে আমি আপনাকে জানাব।</i>")

    else:
        if COMMAND:
            send_tg("নতুন রিসার্চ শুরু করতে চাইলে <b>/start</b> লিখুন।")

if __name__ == "__main__":
    main()
