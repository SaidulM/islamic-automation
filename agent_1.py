import os
import requests
import re

# পরিবেশ ভেরিয়েবল
TG_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

def send_tg(text):
    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text}
    requests.post(url, json=payload)

def get_topics_without_api():
    # এপিআই ছাড়া সরাসরি ইউটিউব সার্চ পেজ থেকে টপিক খোঁজা
    search_query = "islamic+facts+mystery+history+bangla"
    url = f"https://www.youtube.com/results?search_query={search_query}&sp=CAMSAhAB" # sp=... মানে শর্টস ও ভিউ অনুযায়ী ফিল্টার
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers)
        # ভিডিও টাইটেলগুলো খুঁজে বের করার জন্য রেগুলার এক্সপ্রেশন
        titles = re.findall(r'"title":\{"runs":\[\{"text":"(.*?)"\}\]', response.text)
        
        # ইউনিক এবং প্রাসঙ্গিক ৩টি টপিক নেওয়া
        unique_topics = []
        for t in titles:
            if len(t) > 20 and t not in unique_topics: # খুব ছোট টাইটেল বাদ দেওয়া
                unique_topics.append(t)
            if len(unique_topics) == 3:
                break
                
        if not unique_topics:
            return ["ইসলামিক রহস্যময় ঘটনা", "ইতিহাসের অজানা তথ্য", "সেরা ৩টি ইসলামিক উপদেশ"]
            
        return unique_topics
    except:
        return ["ইসলামিক রহস্যময় ঘটনা", "ইতিহাসের অজানা তথ্য", "সেরা ৩টি ইসলামিক উপদেশ"]

command = os.getenv('COMMAND', '').lower()

if command == "/start":
    send_tg("আসসালামু আলাইকুম! আমি ভাইরাল টপিক খুঁজছি (API ছাড়াই)...")
    
    results = get_topics_without_api()
    
    message = "🔍 আমি আজ এই ৩টি ভাইরাল টপিক খুঁজে পেয়েছি:\n\n"
    for i, topic in enumerate(results, 1):
        message += f"{i}. {topic}\n"
    
    message += "\nআপনি কোনটি নিয়ে কাজ করতে চান? (১, ২ বা ৩ লিখে রিপ্লাই দিন)"
    send_tg(message)

elif command in ["1", "2", "3"]:
    send_tg(f"আপনি {command} নম্বর টপিকটি পছন্দ করেছেন। আমি এখন AI দিয়ে স্ক্রিপ্ট লেখা শুরু করছি!")
else:
    if command:
        send_tg("নতুন টপিক খুঁজতে /start লিখুন।")
