"""
Apps Script Gateway-এর সাথে কথা বলার হেল্পার।
GitHub Actions থেকে Sheet পড়তে/লিখতে হলে সব এই ফাইলের ভেতর দিয়ে যাবে
(কোনো Google Service Account লাগে না)।
"""
import os
import requests

APPS_SCRIPT_URL = os.environ["APPS_SCRIPT_URL"]
GATEWAY_API_KEY = os.environ["GATEWAY_API_KEY"]


def _call(action, **kwargs):
    payload = {"action": action, "api_key": GATEWAY_API_KEY, **kwargs}
    resp = requests.post(APPS_SCRIPT_URL, json=payload, timeout=30)
    resp.raise_for_status()
    return resp.json()


def get_pool_topics(count=3):
    return _call("get_pool_topics", count=count).get("topics", [])


def save_pool_topics(topics):
    return _call("save_pool_topics", topics=topics)


def mark_topic_status(topic_id, status):
    return _call("mark_topic_status", id=topic_id, status=status)


def save_script(data):
    return _call("save_script", data=data)


def get_session():
    return _call("get_session")


def set_session(session):
    return _call("set_session", session=session)


def set_job_done():
    return _call("set_job_status", status="done")


def send_telegram_via_gateway(chat_id, text):
    # সাধারণত telegram_utils.py সরাসরি পাঠাবে, এটা fallback হিসেবে রাখা
    return _call("send_message", chat_id=chat_id, text=text)


def log(action_name, details):
    return _call("log", action_name=action_name, details=details)


def pool_count():
    return _call("pool_count").get("count", 0)
