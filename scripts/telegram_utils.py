"""Telegram Bot API-তে সরাসরি মেসেজ পাঠানোর হেল্পার।"""
import os
import requests

TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
BASE = f"https://api.telegram.org/bot{TOKEN}"


def send_message(chat_id, text):
    # Telegram এর মেসেজ লিমিট ৪০৯৬ ক্যারেক্টার — লম্বা স্ক্রিপ্ট হলে ভাগ করে পাঠানো
    for i in range(0, len(text), 4000):
        requests.post(f"{BASE}/sendMessage", json={
            "chat_id": chat_id,
            "text": text[i:i + 4000]
        }, timeout=20)


def send_typing(chat_id):
    requests.post(f"{BASE}/sendChatAction", json={
        "chat_id": chat_id,
        "action": "typing"
    }, timeout=10)
