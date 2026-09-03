import os
import requests

# পরিবেশ ভেরিয়েবল থেকে তথ্য নেওয়া
TG_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
YT_KEY = os.getenv('YOUTUBE_API_KEY')
CHAT_ID = os.getenv('CHAT_ID')

def send_tg(text):
    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text}
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Telegram send error: {e}")

def get_viral_topics():
    # সঠিক YouTube API URL (এখানেই আগে ভুল হয়েছিল)
    search_url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        'part': 'snippet',
        'q': 'Islamic facts stories mystery bangla hindi',
        'maxResults': 3,
        'type': 'video',
        'order': 'viewCount',
        'key': YT_KEY
    }
    
    try:
        response = requests.get(search_url, params=params)
        # যদি API থেকে কোনো ভুল রেসপন্স আসে (যেমন ভুল Key)
        if response.status_code != 200:
            return f"YouTube API Error: {response.status_code} - {response.text}"
            
        data = response.json()
        
        topics = []
        if 'items' in data:
            for item in data['items']:
                title = item['snippet']['title']
                topics.append(title)
        
        if not topics:
            return "দুঃখিত, কোনো টপিক খুঁজে পাওয়া যায়নি। আপনার API Key কি সঠিক?"
            
        return topics
        
    except Exception as e:
        return f"নেটওয়ার্ক বা ডাটা প্রসেসিং সমস্যা: {str(e)}"

command = os.getenv('COMMAND', '').lower()

if command == "/start":
    send_tg("আসসালামু আলাইকুম! আমি রিসার্চ শুরু করছি। একটু অপেক্ষা করুন...")
    
    results = get_viral_topics()
    
    if isinstance(results, str): # যদি এরর মেসেজ আসে
        send_tg(results)
    else:
        message = "🔍 আমি আজ এই ৩টি ভাইরাল টপিক খুঁজে পেয়েছি:\n\n"
        for i, topic in enumerate(results, 1):
            message += f"{i}. {topic}\n"
        
        message += "\nআপনি কোনটি নিয়ে কাজ করতে চান? (১, ২ বা ৩ লিখে রিপ্লাই দিন)"
        send_tg(message)

elif command in ["1", "2", "3"]:
    # এখানে আমরা পরে স্ক্রিপ্ট রাইটিং এজেন্ট যোগ করব
    send_tg(f"আপনি {command} নম্বর টপিকটি পছন্দ করেছেন। আমি এখন স্ক্রিপ্ট লেখা শুরু করছি! (Coming Soon)")
else:
    # যদি অন্য কোনো মেসেজ দেয়
    if command:
        send_tg("নতুন টপিক খুঁজতে /start লিখুন অথবা ১, ২, ৩ লিখে টপিক পছন্দ করুন।")
