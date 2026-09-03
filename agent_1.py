import os
import requests

# পরিবেশ ভেরিয়েবল থেকে তথ্য নেওয়া
TG_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
YT_KEY = os.getenv('YOUTUBE_API_KEY')
CHAT_ID = os.getenv('CHAT_ID')

def send_tg(text):
    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text}
    requests.post(url, json=payload)

def get_viral_topics():
    # সরাসরি API URL ব্যবহার করে তথ্য আনা (গুগল লাইব্রেরি ছাড়া)
    search_url = "https://www.googleapis.com/api/v3/search"
    params = {
        'part': 'snippet',
        'q': 'Islamic facts status| mysterious islamic stories bangla',
        'maxResults': 3,
        'type': 'video',
        'order': 'viewCount',
        'key': YT_KEY
    }
    
    response = requests.get(search_url, params=params)
    data = response.json()
    
    # এরর চেক করা
    if 'error' in data:
        return f"API Error: {data['error']['message']}"
    
    topics = []
    for item in data.get('items', []):
        title = item['snippet']['title']
        topics.append(title)
    return topics

command = os.getenv('COMMAND', '').lower()

if command == "/start":
    send_tg("আসসালামু আলাইকুম! আমি রিসার্চ শুরু করছি। একটু অপেক্ষা করুন...")
    try:
        results = get_viral_topics()
        
        if isinstance(results, str): # যদি এরর মেসেজ আসে
            send_tg(results)
        else:
            message = "🔍 আমি আজ এই ৩টি ভাইরাল টপিক খুঁজে পেয়েছি:\n\n"
            for i, topic in enumerate(results, 1):
                message += f"{i}. {topic}\n"
            
            message += "\nআপনি কোনটি নিয়ে কাজ করতে চান? (১, ২ বা ৩ লিখে রিপ্লাই দিন)"
            send_tg(message)
            
    except Exception as e:
        send_tg(f"সমস্যা হয়েছে: {str(e)}")

elif command in ["1", "2", "3"]:
    send_tg(f"আপনি {command} নম্বর টপিকটি পছন্দ করেছেন। আমি এখন স্ক্রিপ্ট লেখা শুরু করছি! (Coming Soon)")
else:
    send_tg("আপনি নতুন টপিক চাইলে /start লিখুন।")
