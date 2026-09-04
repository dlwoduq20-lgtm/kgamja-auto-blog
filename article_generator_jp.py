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
    "gemini-3-flash-preview",
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite"
]


def generate_article_jp(topic: str) -> dict:
    """
    Generate a full SEO-optimized Japanese article matching Japanese Google SEO and reader intent.
    """
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY is not set.")

    client = genai.Client(api_key=GEMINI_API_KEY)
    user_prompt = f"以下のテーマについて、読者のピンチを解決する実体験談＋具体的マニュアル形式のブログ記事を作成してください：\nテーマ: {topic}"

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
