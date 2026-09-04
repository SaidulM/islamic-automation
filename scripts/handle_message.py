"""
মূল কনভারসেশন লজিক। repository_dispatch (telegram_message) বা
scheduled cron থেকে ট্রিগার হয়ে চলে।

State machine (Apps Script PropertiesService-এ session হিসেবে জমা থাকে):
  idle                  → কিছু pending নেই
  awaiting_topic_choice → ৩টা টপিক পাঠানো হয়েছে, নাম্বার/টেক্সটের অপেক্ষা
  awaiting_script_approval → স্ক্রিপ্ট পাঠানো হয়েছে, approve/reject-এর অপেক্ষা
"""
import os
import sys
import threading
import time
import difflib

from scripts import sheet_client, telegram_utils, llm_client

CHAT_ID = os.environ["CHAT_ID"]
TEXT = os.environ.get("MESSAGE_TEXT", "").strip()
TRIGGER_SOURCE = os.environ.get("TRIGGER_SOURCE", "telegram")  # telegram | scheduled

# ============================================================
# টাইপিং ইন্ডিকেটর — GitHub Action চলাকালীন প্রতি ৪ সেকেন্ডে "typing"
# পাঠাতে থাকে একটা আলাদা background thread-এ, যতক্ষণ না কাজ শেষ হয়।
# (Apps Script আর অপেক্ষা করে না, তাই এই দায়িত্ব এখন এখানে)
# ============================================================
_stop_typing = threading.Event()


def _typing_loop():
    while not _stop_typing.is_set():
        telegram_utils.send_typing(CHAT_ID)
        _stop_typing.wait(4)


_typing_thread = threading.Thread(target=_typing_loop, daemon=True)
_typing_thread.start()

START_WORDS = {"start", "শুরু", "/start"}
APPROVE_WORDS = {"approve", "ঠিক আছে", "পছন্দ হয়েছে", "হ্যাঁ", "ok", "okay"}
REJECT_WORDS = {"না", "পছন্দ হয়নি", "regenerate", "আবার", "again", "reject"}


def finish():
    _stop_typing.set()
    sys.exit(0)


def send_topics():
    topics = sheet_client.get_pool_topics(count=3)
    if len(topics) < 3:
        telegram_utils.send_message(CHAT_ID, "⚠️ পুল-এ পর্যাপ্ত টপিক নেই, একটু পরে আবার চেষ্টা করুন (fetch_topic_pool.yml রান হওয়ার অপেক্ষায়)।")
        finish()

    msg = "🕌 আজকের ৩টা টপিক অপশন:\n\n"
    for i, t in enumerate(topics, 1):
        msg += f"{i}. {t['topic']}\n"
    msg += "\nনাম্বার লিখুন (1/2/3), অথবা কোনোটাই পছন্দ না হলে 'না' লিখুন নতুন টপিকের জন্য।"

    telegram_utils.send_message(CHAT_ID, msg)
    sheet_client.set_session({"state": "awaiting_topic_choice", "shown_topics": topics})


def match_topic(text, shown_topics):
    text = text.strip()
    if text in {"1", "2", "3"}:
        idx = int(text) - 1
        if idx < len(shown_topics):
            return shown_topics[idx]
    # ফাজি ম্যাচ — user টপিক কপি-পেস্ট করলে
    best, best_ratio = None, 0.0
    for t in shown_topics:
        ratio = difflib.SequenceMatcher(None, text.lower(), t["topic"].lower()).ratio()
        if ratio > best_ratio:
            best, best_ratio = t, ratio
    return best if best_ratio > 0.6 else None


def handle_topic_choice(session):
    shown = session.get("shown_topics", [])

    if TEXT.lower() in REJECT_WORDS or TEXT in {"না"}:
        sheet_client.log("Topic_Rejected", "সব টপিক বাদ, নতুন খোঁজা হচ্ছে")
        send_topics()
        finish()

    matched = match_topic(TEXT, shown)
    if not matched:
        telegram_utils.send_message(CHAT_ID, "টপিকটা বুঝতে পারলাম না। 1/2/3 লিখুন, অথবা টপিক কপি করে পেস্ট করুন।")
        finish()

    sheet_client.mark_topic_status(matched["id"], "Approved")

    hindi_script = llm_client.generate_script(matched["topic"])
    hindi_script = llm_client.humanize(hindi_script)
    summary_bn = llm_client.bengali_summary(hindi_script)

    msg = f"✅ টপিক: {matched['topic']}\n\n📝 সংক্ষেপে (বাংলা): {summary_bn}\n\n---\n{hindi_script}\n---\n\nস্ক্রিপ্ট পছন্দ হলে 'approve' লিখুন, না হলে 'আবার' লিখুন নতুন ভার্সনের জন্য।"
    telegram_utils.send_message(CHAT_ID, msg)

    sheet_client.set_session({
        "state": "awaiting_script_approval",
        "current_topic": matched,
        "current_script": hindi_script,
        "regenerate_count": 0,
    })


def handle_script_approval(session):
    topic = session["current_topic"]
    script = session["current_script"]

    if TEXT.lower() in APPROVE_WORDS or TEXT in {"হ্যাঁ"}:
        meta = llm_client.generate_metadata(topic["topic"], script)
        sheet_client.save_script({
            "topic_id": topic["id"],
            "topic_en": topic["topic"],
            "hindi_script": script,
            "title_en": meta["title"],
            "description_en": meta["description"],
            "tags": meta["tags"],
            "hashtags": meta["hashtags"],
        })
        msg = (
            f"🎉 সেভ হয়ে গেছে Sheet-এ!\n\n"
            f"Title: {meta['title']}\n"
            f"Description: {meta['description']}\n"
            f"Tags: {meta['tags']}\n"
            f"Hashtags: {meta['hashtags']}"
        )
        telegram_utils.send_message(CHAT_ID, msg)
        sheet_client.set_session({"state": "idle"})
        finish()

    if TEXT.lower() in REJECT_WORDS:
        count = session.get("regenerate_count", 0) + 1
        new_script = llm_client.humanize(llm_client.generate_script(topic["topic"]))
        summary_bn = llm_client.bengali_summary(new_script)

        msg = f"🔄 নতুন ভার্সন (#{count}):\n\n📝 বাংলা: {summary_bn}\n\n---\n{new_script}\n---\n\n'approve' বা 'আবার' লিখুন।"
        telegram_utils.send_message(CHAT_ID, msg)

        session["current_script"] = new_script
        session["regenerate_count"] = count
        sheet_client.set_session(session)
        finish()

    telegram_utils.send_message(CHAT_ID, "'approve' লিখুন (পছন্দ হলে) অথবা 'আবার' লিখুন (নতুন ভার্সনের জন্য)।")


def main():
    session = sheet_client.get_session()
    state = session.get("state", "idle")

    # "start" যেকোনো অবস্থাতেই নতুন করে শুরু করে
    if TEXT.lower() in START_WORDS:
        if TRIGGER_SOURCE == "scheduled" and state != "idle":
            sheet_client.log("Scheduled_Skipped", f"session busy (state={state}), শিডিউল করা মেসেজ স্কিপ করা হলো")
            finish()
        send_topics()
        finish()

    if state == "awaiting_topic_choice":
        handle_topic_choice(session)
    elif state == "awaiting_script_approval":
        handle_script_approval(session)
    else:
        telegram_utils.send_message(CHAT_ID, "'start' লিখুন নতুন টপিক পেতে।")

    finish()


if __name__ == "__main__":
    main()
