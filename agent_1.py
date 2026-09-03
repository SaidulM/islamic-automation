import os
import requests
from googleapiclient.discovery import build

# পরিবেশ ভেরিয়েবল থেকে তথ্য নেওয়া
TG_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
YT_KEY = os.getenv('YOUTUBE_API_KEY')
CHAT_ID = os.getenv('CHAT_ID')

def send_tg(text):
    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": CHAT_ID, "text": text})

def get_viral_topics():
    youtube = build('youtube', 'v3', developerKey=YT_KEY)
    
    # ইসলামিক ভাইরাল টপিক খোঁজা (Shorts/Videos)
    request = youtube.search().list(
        q="Islamic facts bangla status| islamic emotional story hindi",
        part="snippet",
        maxResults=3,
        type="video",
        order="viewCount",
        publishedAfter="2024-01-01T00:00:00Z"
    )
    response = request.execute()
    
    topics = []
    for item in response['items']:
        title = item['snippet']['title']
        topics.append(title)
    return topics

command = os.getenv('COMMAND', '').lower()

if command == "/start":
    send_tg("আসসালামু আলাইকুম! আমি রিসার্চ শুরু করছি। একটু অপেক্ষা করুন...")
    try:
        results = get_viral_topics()
        message = "🔍 আমি আজ এই ৩টি ভাইরাল টপিক খুঁজে পেয়েছি:\n\n"
        for i, topic in enumerate(results, 1):
            message += f"{i}. {topic}\n"
        
        message += "\nআপনি কোনটি নিয়ে কাজ করতে চান? (১, ২ বা ৩ লিখে রিপ্লাই দিন)"
        send_tg(message)
    except Exception as e:
        send_tg(f"রিসার্চ করতে সমস্যা হয়েছে: {str(e)}")

elif command in ["1", "2", "3"]:
    send_tg(f"আপনি {command} নম্বর টপিকটি পছন্দ করেছেন। আমি এখন স্ক্রিপ্ট লেখা শুরু করছি! (Coming Soon)")
else:
    send_tg("আপনি নতুন টপিক চাইলে /start লিখুন।")
