"""
Article Generator using Gemini API with reliable flash models and retry backoff
"""
import json
import re
import time
from google import genai
from google.genai import types
from config import GEMINI_API_KEY
from prompt_template import SYSTEM_PROMPT

MODELS = [
    "gemini-3.1-flash-lite",
    "gemini-2.5-flash-lite",
    "gemini-3-flash-preview"
]


def generate_article(topic: str) -> dict:
    """
    Generate a full SEO-optimized article matching kgamjablog's DNA.
    """
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY is not set.")

    client = genai.Client(api_key=GEMINI_API_KEY)
    user_prompt = f"다음 주제/키워드에 대해 독자에게 실질적인 해결책을 주는 고품질 블로그 글을 작성해 주세요:\n주제: {topic}"

    last_error = None
    for model_name in MODELS:
        for attempt in range(2):
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=user_prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_PROMPT,
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
                    raise ValueError(f"Invalid JSON response")

            except Exception as e:
                last_error = e
                print(f"⚠️ {model_name} (시도 {attempt+1}) 일시적 오류: {e}. 잠시 후 재시도...")
                time.sleep(2)

    raise RuntimeError(f"All models failed to generate article: {last_error}")
