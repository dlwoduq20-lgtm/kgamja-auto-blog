"""
Japanese Article Generator using Gemini API with reliable flash models and retry backoff
"""
import json
import re
import time
from google import genai
from google.genai import types
from config import GEMINI_API_KEY
from prompt_template_jp import SYSTEM_PROMPT_JP

MODELS = [
    "gemini-3.1-flash-lite",
    "gemini-2.5-flash-lite",
    "gemini-3-flash-preview"
]


def generate_article_jp(topic: str, related_articles: list = None) -> dict:
    """
    Generate a full SEO-optimized Japanese article matching Japanese Google SEO, E-E-A-T, and internal links.
    """
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY is not set.")

    client = genai.Client(api_key=GEMINI_API_KEY)
    
    links_text = ""
    if related_articles:
        links_text = "\n[内部リンク候補記事リスト (Contextual Internal Linking)]\n" + "\n".join(
            [f"- 記事: '{a.get('title')}' -> URL: {a.get('url')}" for a in related_articles[:3]]
        ) + "\n上記リストから本文の文脈に最も合致する1〜2件を選び、本文中に <a href='URL'>記事タイトル</a> の形式で自然な案内リンクボックスを挿入してください。\n"

    user_prompt = (
        f"以下のテーマについて、読者のピンチを解決する実体験談＋具体的マニュアル形式のブログ記事を作成してください：\nテーマ: {topic}\n"
        f"必ず日本の法令・判例基準のE-E-A-T監修基準ボックス、動的H2/H3見出し、実務比較/手順<table>表を含めてください。{links_text}"
    )

    last_error = None
    for model_name in MODELS:
        for attempt in range(2):
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=user_prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_PROMPT_JP,
                        temperature=0.7,
                        response_mime_type="application/json"
                    )
                )

                raw_text = response.text.strip()
                try:
                    data = json.loads(raw_text)
                    return data
                except Exception:
                    json_match = re.search(r'\{.*\}', raw_text, re.DOTALL)
                    if json_match:
                        return json.loads(json_match.group(0))
                    raise ValueError("Invalid JSON response")

            except Exception as e:
                last_error = e
                print(f"⚠️ {model_name} (試行 {attempt+1}) 一時的エラー: {e}. 再試行中...")
                time.sleep(2)

    raise RuntimeError(f"All models failed to generate article: {last_error}")
