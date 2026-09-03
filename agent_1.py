import os
import requests

def send_telegram_message(text):
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('CHAT_ID')
    if not chat_id: return # যদি ক্রন জব থেকে রান হয়
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    requests.post(url, json=payload)

command = os.getenv('COMMAND')
print(f"Received command: {command}")

if command == "/start":
    send_telegram_message("আসসালামু আলাইকুম! আমি আপনার AI এজেন্ট। আমি এখন কাজ করার জন্য প্রস্তুত।")
else:
    send_telegram_message(f"আপনি বলেছেন: {command}। আমি এখনো শিখছি, খুব শীঘ্রই আমি রিসার্চ শুরু করতে পারব!")
