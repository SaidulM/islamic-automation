"""
Groq API (সম্পূর্ণ ফ্রি, কোনো কার্ড লাগে না, LPU hardware-এ চলে বলে
সেকেন্ডে রেসপন্স দেয়) দিয়ে script generation, humanize পাস, metadata।

মডেল: llama-3.3-70b-versatile — কোনো ডাউনলোড/ক্যাশ লাগে না, প্রতিটা
কল সরাসরি Groq-এর সার্ভারে যায়।
"""
import os
import requests

GROQ_API_KEY = os.environ["GROQ_API_KEY"]
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "llama-3.3-70b-versatile"


def _chat(system_prompt, user_prompt, max_tokens=900, temperature=0.8):
    resp = requests.post(
        GROQ_URL,
        headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
        json={
            "model": MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "max_tokens": max_tokens,
            "temperature": temperature,
        },
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"].strip()


def generate_script(topic_en):
    """৮ সিন সাসপেন্সফুল হিন্দি স্ক্রিপ্ট, Quran/Hadith রেফারেন্স সহ"""
    system = (
        "You are an expert scriptwriter for Islamic short-form (60s) YouTube videos in Hindi. "
        "Format: 8 scenes, suspenseful pacing, a strong 3-second hook, verified Quran citations "
        "(surah name + ayat number) and/or hadith citations (collection + hadith number), "
        "ending with an Islamic moral conclusion. Write naturally, like a human storyteller — "
        "avoid robotic or overly formal AI-sounding phrasing."
    )
    user = f"Topic: {topic_en}\n\nWrite the full Hindi script now, scene by scene (Scene 1 to Scene 8)."
    return _chat(system, user, max_tokens=900, temperature=0.85)


def humanize(hindi_script):
    """স্ক্রিপ্টটা আরেকবার ঘষামাজা করে আরও স্বাভাবিক/মানুষের মতো করা"""
    system = (
        "You polish Hindi scripts to sound naturally human-written — vary sentence rhythm, "
        "remove repetitive AI patterns, keep the meaning and citations exactly the same."
    )
    user = f"Rewrite this script so it reads more naturally, human, and emotionally engaging:\n\n{hindi_script}"
    return _chat(system, user, max_tokens=900, temperature=0.7)


def bengali_summary(hindi_script):
    """স্ক্রিপ্টের সংক্ষিপ্ত বাংলা বর্ণনা (রিভিউর জন্য)"""
    system = "You summarize Hindi video scripts in 2-3 sentences of natural Bengali, for the creator's quick review."
    user = f"Script:\n{hindi_script}\n\nSummarize in Bengali (2-3 sentences)."
    return _chat(system, user, max_tokens=200, temperature=0.6)


def generate_metadata(topic_en, hindi_script):
    """Title, description, tags, hashtags — English, YouTube/Facebook উপযোগী"""
    system = (
        "You write viral, click-worthy YouTube/Facebook metadata for Islamic short videos. "
        "Return exactly in this format:\nTITLE: ...\nDESCRIPTION: ...\nTAGS: tag1, tag2, ...\nHASHTAGS: #tag1 #tag2 ..."
    )
    user = f"Topic: {topic_en}\n\nScript:\n{hindi_script}\n\nGenerate the metadata now."
    raw = _chat(system, user, max_tokens=400, temperature=0.8)

    data = {"title": "", "description": "", "tags": "", "hashtags": ""}
    for line in raw.split("\n"):
        if line.upper().startswith("TITLE:"):
            data["title"] = line.split(":", 1)[1].strip()
        elif line.upper().startswith("DESCRIPTION:"):
            data["description"] = line.split(":", 1)[1].strip()
        elif line.upper().startswith("TAGS:"):
            data["tags"] = line.split(":", 1)[1].strip()
        elif line.upper().startswith("HASHTAGS:"):
            data["hashtags"] = line.split(":", 1)[1].strip()
    return data
