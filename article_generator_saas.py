'''
US/Global B2B SaaS Article Generator using Gemini API
Produces deep, high-converting software reviews and comparison guides.
'''
import json
import re
import time
from google import genai
from google.genai import types
from config import GEMINI_API_KEY
from prompt_template_saas import SYSTEM_PROMPT_SAAS

MODELS = [
    "gemini-3.1-flash-lite",
    "gemini-2.5-flash-lite",
    "gemini-3-flash-preview"
]


def generate_article_saas(keyword: str, topic_angle: str = "", related_articles: list = None) -> dict:
    '''
    Generate a full SEO-optimized B2B SaaS software review and comparison guide.
    '''
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY is not set.")

    client = genai.Client(api_key=GEMINI_API_KEY)
    angle_text = f"\nSpecific angle/focus: {topic_angle}" if topic_angle else ""
    
    links_text = ""
    if related_articles:
        links_text = "\n[INTERNAL LINKING CANDIDATES]\n" + "\n".join(
            [f"- Guide: '{a.get('title')}' -> URL: {a.get('url')}" for a in related_articles[:3]]
        ) + "\nSeamlessly embed 1 or 2 contextual internal links into appropriate sections using <a href='URL'>Title</a>.\n"

    user_prompt = (
        f"Write a comprehensive, SEO-optimized B2B software buyer guide targeting the primary keyword: '{keyword}'.{angle_text}\n"
        f"Target audience: English-speaking small business owners, operations managers, and startup founders in US/UK/CA/AU.\n"
        f"Ensure to include a comparison table of 5-7 leading tools, pricing breakdowns, standout features, limitations, and an actionable buyer checklist.{links_text}"
    )

    last_error = None
    for model_name in MODELS:
        for attempt in range(2):
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=user_prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_PROMPT_SAAS,
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
                    raise ValueError("Invalid JSON response from model")

            except Exception as e:
                last_error = e
                print(f"⚠️ {model_name} (Attempt {attempt+1}) temporary error: {e}. Retrying...")
                time.sleep(2)

    raise RuntimeError(f"All models failed to generate SaaS article: {last_error}")
