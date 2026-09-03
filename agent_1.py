import os
import requests
import re

# Credentials
TG_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')
COMMAND = os.getenv('COMMAND', '').strip()

def send_tg(text):
    if not TG_TOKEN or not CHAT_ID: return
    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"}
    requests.post(url, json=payload)

def get_viral_topics():
    # সরাসরি ইউটিউব থেকে রিসার্চ
    search_query = "islamic+facts+mystery+history+bangla"
    url = f"https://www.youtube.com/results?search_query={search_query}"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        # টাইটেল এক্সট্রাক্ট করার জন্য উন্নত Regex
        raw_titles = re.findall(r'"title":\{"runs":\[\{"text":"(.*?)"\}\]', response.text)
        
        topics = []
        for t in raw_titles:
            # খুব ছোট বা অপ্রাসঙ্গিক টাইটেল বাদ দেওয়া
            if len(t) > 35 and t not in topics:
                topics.append(t)
            if len(topics) == 3: break
        
        # যদি ইউটিউব থেকে না পাওয়া যায়, তবে ৩টি ডিফল্ট ভাইরাল টপিক
        if not topics:
            topics = [
                "পবিত্র কাবার ভেতরে কি আছে? যা জানলে আপনি অবাক হবেন",
                "ইতিহাসের শ্রেষ্ঠ ৫ জন মুসলিম বিজ্ঞানী এবং তাদের আবিষ্কার",
                "কিয়ামতের আগে দাজ্জাল যে স্থানে আত্মপ্রকাশ করবে"
            ]
        return topics
    except:
        return ["ইসলামিক রহস্যময় ঘটনা", "ইতিহাসের অজানা তথ্য", "সেরা ৩টি ইসলামিক উপদেশ"]

def main():
    if not COMMAND: return

    if COMMAND.lower() == "/start":
        send_tg("🌙 <b>আসসালামু আলাইকুম!</b>\nআমি ভাইরাল ইসলামিক টপিক রিসার্চ করছি...")
        topics = get_viral_topics()
        
        msg = "🔍 <b>আমি আজ এই ৩টি ভাইরাল টপিক খুঁজে পেয়েছি:</b>\n\n"
        for i, t in enumerate(topics, 1):
            msg += f"<b>{i}.</b> {t}\n"
        
        msg += "\nআপনি কোনটি নিয়ে কাজ করতে চান? <b>১, ২ বা ৩</b> লিখে রিপ্লাই দিন।"
        send_tg(msg)

    elif COMMAND in ["1", "2", "3"]:
        send_tg(f"✅ আপনি <b>টপিক {COMMAND}</b> পছন্দ করেছেন।\nআমি এখন স্ক্রিপ্ট রাইটিং ইঞ্জিন (Qwen2.5) লোড করছি। একটু অপেক্ষা করুন...")
        # পরবর্তী ধাপে এখানে স্ক্রিপ্ট জেনারেটর কল হবে
    else:
        # অযথা মেসেজে যাতে গিটহাব রান না হয়, তাই ছোট রেসপন্স
        print(f"Unknown command: {COMMAND}")

if __name__ == "__main__":
    main()
