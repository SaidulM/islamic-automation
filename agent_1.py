import os
import requests
import re
import random
import html

# পরিবেশ ভেরিয়েবল (Environment Variables)
TG_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')
COMMAND = os.getenv('COMMAND', '').strip()

def send_tg(text):
    """টেলিগ্রামে মেসেজ পাঠানোর নিরাপদ ফাংশন"""
    if not TG_TOKEN or not CHAT_ID: 
        print("Error: Token or Chat ID is missing!")
        return
        
    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"}
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"Telegram Network Error: {e}")

def get_viral_topics():
    """ইউটিউব থেকে ট্রেন্ডিং ইসলামিক টপিক খোঁজার ফাংশন"""
    queries = [
        "islamic+facts+mystery+history+bangla",
        "mysterious+islamic+stories+hindi+bangla",
        "unknown+islamic+history+facts",
        "prophet+stories+facts+bangla"
    ]
    search_query = random.choice(queries) 
    
    url = f"https://www.youtube.com/results?search_query={search_query}"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"}
    
    try:
        response = requests.get(url, headers=headers, timeout=12)
        raw_titles = re.findall(r'"title":\{"runs":\[\{"text":"(.*?)"\}\]', response.text)
        
        valid_topics = []
        for t in raw_titles:
            # HTML কোড (যেমন &quot;) ক্লিন করা
            clean_title = html.unescape(t)
            
            # খুব ছোট বা অপ্রাসঙ্গিক টাইটেল বাদ দেওয়া
            if len(clean_title) > 30 and clean_title not in valid_topics:
                valid_topics.append(clean_title)
        
        # লিস্ট ওলটপালট করা
        random.shuffle(valid_topics)
        topics = valid_topics[:3]
        
        # যদি কোনো কারণে লিস্ট খালি থাকে
        if not topics:
            raise ValueError("No valid topics found from scraping.")
            
        return topics
        
    except Exception as e:
        print(f"Scraping failed, using fallback. Reason: {e}")
        # ফলব্যাক/ব্যাকআপ টপিক (যদি স্ক্র্যাপিং কাজ না করে)
        fallback_topics = [
            "পবিত্র কাবার ভেতরের অজানা রহস্য",
            "ইতিহাসের পাতায় হারানো মুসলিম বীরদের কাহিনী",
            "ভবিষ্যতের দাজ্জাল এবং বর্তমান পৃথিবী"
        ]
        random.shuffle(fallback_topics)
        return fallback_topics

def main():
    if not COMMAND: 
        return
        
    cmd = COMMAND.lower()

    # কমান্ড অনুযায়ী কাজ করা (Start বা Reject)
    if cmd in ["/start", "না", "na", "no", "আরো", "more"]:
        send_tg("🔍 <b>নতুন ইসলামিক টপিক রিসার্চ করছি...</b>\nএকটু অপেক্ষা করুন।")
        
        topics = get_viral_topics()
        
        msg = "🔍 <b>আপনার জন্য এই ৩টি টপিক খুঁজে পেয়েছি:</b>\n\n"
        for i, t in enumerate(topics, 1):
            msg += f"<b>{i}.</b> {t}\n"
        
        msg += "\n✅ পছন্দ হলে <b>১, ২ বা ৩</b> লিখে পাঠান।\n❌ পছন্দ না হলে <b>'না'</b> লিখে পাঠান।"
        send_tg(msg)

    # ইউজার যদি ১, ২ বা ৩ সিলেক্ট করে (বাংলা বা ইংরেজি সংখ্যা)
    elif cmd in ["1", "2", "3", "১", "২", "৩"]:
        
        # বাংলা সংখ্যাকে ইংরেজিতে কনভার্ট করা (লজিকের সুবিধার জন্য)
        bengali_to_eng = {"১": "1", "২": "2", "৩": "3"}
        selected_number = bengali_to_eng.get(cmd, cmd)
        
        send_tg(f"✅ আপনি <b>টপিক {selected_number}</b> পছন্দ করেছেন।\n\n🧠 <b>এখন আমি এটি নিয়ে স্ক্রিপ্ট লিখছি...</b>\n<i>(এতে ১-২ মিনিট সময় লাগতে পারে)</i>")
        
        # **নেক্সট স্টেপ:** এখানে Qwen AI দিয়ে স্ক্রিপ্ট লেখার কোড বসবে
        
    else:
        # অপ্রয়োজনীয় মেসেজ ইগনোর করা, যাতে গিটহাব অ্যাকশন ফেইল না করে
        print(f"Ignored unknown command: {COMMAND}")

if __name__ == "__main__":
    main()
