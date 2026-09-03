import os
import requests

# পরিবেশ ভেরিয়েবল থেকে তথ্য নেওয়া
TG_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
YT_KEY = os.getenv('YOUTUBE_API_KEY')
CHAT_ID = os.getenv('CHAT_ID')

# চেক করা চাবিটি আদেও আছে কি না (এটি গিটহাব অ্যাকশন লগে দেখাবে)
if not YT_KEY:
    print("Error: YOUTUBE_API_KEY not found in environment variables!")
else:
    print(f"API Key found! Starts with: {YT_KEY[:5]}...") # নিরাপত্তার খাতিরে শুধু প্রথম ৫ অক্ষর প্রিন্ট করবে

def send_tg(text):
    # বাকি কোড আগের মতোই থাকবে...
