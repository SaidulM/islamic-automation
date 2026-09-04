"""
Qwen2.5-3B-Instruct (GGUF, quantized) দিয়ে লোকাল inference — সম্পূর্ণ ফ্রি,
কোনো API key লাগে না। মডেল ফাইলটা workflow-এর মধ্যে cache/download হয়ে
MODEL_PATH-এ রেডি থাকে (দেখুন .github/workflows/)।

⚠️ নোট: GitHub Actions-এর ফ্রি রানারে GPU নেই, তাই CPU-তে চলে — একটা
স্ক্রিপ্ট জেনারেট হতে ১-৫ মিনিট লাগতে পারে। এটাই কেন Apps Script "typing"
loop-টা দরকার (ব্যবহারকারী বসে বসে টাইপিং দেখবে, ফলাফলের অপেক্ষায়)।
"""
import os
from llama_cpp import Llama

MODEL_PATH = os.environ.get("MODEL_PATH", "./models/qwen2.5-3b-instruct-q4_k_m.gguf")

_llm = None


def _get_llm():
    global _llm
    if _llm is None:
        _llm = Llama(model_path=MODEL_PATH, n_ctx=4096, n_threads=2, verbose=False)
    return _llm


def _chat(system_prompt, user_prompt, max_tokens=700, temperature=0.8):
    llm = _get_llm()
    result = llm.create_chat_completion(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        max_tokens=max_tokens,
        temperature=temperature,
    )
    return result["choices"][0]["message"]["content"].strip()


def suggest_topics(seed_titles, n=50):
    """YouTube-এ trending Islamic শর্ট ভিডিওর টাইটেল দেখে নতুন, unique টপিক আইডিয়া বানানো (কপি না করে)"""
    system = (
        "You are a content strategist for Islamic short-form YouTube videos (60 seconds, Hindi audience). "
        "You generate ORIGINAL topic ideas inspired by trends, never copying existing titles."
    )
    user = (
        f"Here are some currently trending Islamic short-video titles:\n"
        f"{chr(10).join('- ' + t for t in seed_titles[:20])}\n\n"
        f"Suggest {n} NEW, original topic ideas for 60-second Islamic short videos "
        f"(Quranic teachings, hadith-based motivation, or Islamic cartoon storytelling). "
        f"One topic per line, in English, no numbering, no explanation."
    )
    raw = _chat(system, user, max_tokens=1200, temperature=0.9)
    lines = [l.strip("-• ").strip() for l in raw.split("\n") if l.strip()]
    return lines[:n]


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
