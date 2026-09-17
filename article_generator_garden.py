'''
Home & Garden Article Generator using Gemini API
Generates comprehensive, E-E-A-T rich horticulture guides with embedded pastel vector illustrations.
'''
import json
import re
import time
import base64
from google import genai
from google.genai import types
from config import GEMINI_API_KEY
from prompt_template_garden import SYSTEM_PROMPT_GARDEN, USER_PROMPT_TEMPLATE_GARDEN
from image_manager_garden import fetch_garden_image_bytes

MODELS = [
    "gemini-3.1-flash-lite",
    "gemini-2.5-flash-lite",
    "gemini-3-flash-preview"
]


def generate_article_garden(keyword: str, topic_angle: str = "", avoid_topics: list = None, competitor_urls: str = "None", related_articles: list = None) -> dict:
    '''
    Generate a complete SEO-optimized Home & Garden article with images and schema markup.
    '''
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY is not set.")

    client = genai.Client(api_key=GEMINI_API_KEY)
    avoid_str = ", ".join(avoid_topics) if avoid_topics else "None"

    links_text = ""
    if related_articles:
        links_text = "\n\n[INTERNAL LINKING CANDIDATES]\n" + "\n".join(
            [f"- Guide: '{a.get('title')}' -> URL: {a.get('url')}" for a in related_articles[:3]]
        ) + "\nSeamlessly embed 1 or 2 contextual internal links into appropriate sections using <a href='URL'>Title</a>.\n"

    formatted_user_prompt = (
        USER_PROMPT_TEMPLATE_GARDEN
        .replace("{KEYWORD}", keyword)
        .replace("{TOPIC}", topic_angle or f"Complete practical guide to {keyword} for home gardeners")
        .replace("{COMPETITOR_URLS}", competitor_urls)
        .replace("{AVOID_TOPICS}", avoid_str)
    ) + links_text

    last_error = None
    data = None

    for model_name in MODELS:
        for attempt in range(2):
            try:
                print(f"[AI Writer] Calling {model_name} for '{keyword}'...")
                response = client.models.generate_content(
                    model=model_name,
                    contents=formatted_user_prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_PROMPT_GARDEN,
                        temperature=0.7,
                        response_mime_type="application/json"
                    )
                )

                raw_text = response.text.strip()
                try:
                    data = json.loads(raw_text)
                    break
                except Exception:
                    json_match = re.search(r'\{.*\}', raw_text, re.DOTALL)
                    if json_match:
                        data = json.loads(json_match.group(0))
                        break
                    raise ValueError("Invalid JSON response from model")

            except Exception as e:
                last_error = e
                print(f"⚠️ {model_name} (Attempt {attempt+1}) temporary error: {e}. Retrying...")
                time.sleep(2)

        if data:
            break

    if not data:
        raise RuntimeError(f"All models failed to generate Garden article: {last_error}")

    # Process and embed pastel vector illustrations
    images_spec = data.get("images", [])
    content_html = data.get("content_html") or ""
    if not content_html and data.get("body_markdown"):
        try:
            import markdown
            content_html = markdown.markdown(data.get("body_markdown"), extensions=['tables', 'nl2br'])
        except Exception as e:
            print(f"⚠️ Markdown conversion warning: {e}")
            content_html = data.get("body_markdown")

    h1_title = data.get("h1", keyword)
    hero_bytes = None

    print(f"\n🎨 [Illustrations] Generating style-locked pastel illustrations (Total: {len(images_spec)} planned)...", flush=True)

    # Generate images (limit to primary hero + 1-2 body images for optimal speed and reliability)
    embedded_count = 0
    for idx, img_info in enumerate(images_spec[:3]):
        gen_prompt = img_info.get("generation_prompt") or f"{keyword} gardening illustration"
        placement_h2 = img_info.get("placement", "")
        alt_text = img_info.get("alt_text", f"{keyword} guide illustration")
        caption = img_info.get("caption") or ""

        print(f"   [{idx+1}/{min(3, len(images_spec))}] Generating image for: {img_info.get('purpose', 'guide')}...")
        img_bytes = fetch_garden_image_bytes(gen_prompt)

        if not img_bytes:
            continue

        if idx == 0:
            hero_bytes = img_bytes

        b64_str = base64.b64encode(img_bytes).decode('utf-8')
        caption_html = f'<p style="color: #666; font-size: 13px; margin-top: 8px; text-align: center; font-style: italic;">▲ {caption}</p>' if caption else ''
        img_block = (
            f'\n<div style="text-align: center; margin: 32px auto; max-width: 720px;">\n'
            f'  <img src="data:image/jpeg;base64,{b64_str}" alt="{alt_text}" '
            f'style="width: 100%; height: auto; border-radius: 12px; box-shadow: 0 4px 16px rgba(0,0,0,0.08);" />\n'
            f'  {caption_html}\n'
            f'</div>\n'
        )

        # Place after relevant H2 if found, else prepend or append
        if placement_h2 and placement_h2.lower() in content_html.lower():
            # Find the closing </h2> tag corresponding to placement_h2
            pattern = re.compile(rf'(<h2[^>]*>.*?{re.escape(placement_h2)}.*?</h2>)', re.IGNORECASE)
            if pattern.search(content_html):
                content_html = pattern.sub(rf'\1\n{img_block}', content_html, count=1)
                embedded_count += 1
                continue

        # If placement not matched or it is the hero image, prepend to content
        if idx == 0 and img_block not in content_html:
            content_html = img_block + content_html
            embedded_count += 1

    # Inject FAQ Schema Markup
    faq_schema_items = data.get("faq_schema", [])
    if faq_schema_items:
        faq_ld = {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": [
                {
                    "@type": "Question",
                    "name": item.get("question", ""),
                    "acceptedAnswer": {
                        "@type": "Answer",
                        "text": item.get("answer", "")
                    }
                } for item in faq_schema_items if item.get("question") and item.get("answer")
            ]
        }
        content_html += f'\n<script type="application/ld+json">\n{json.dumps(faq_ld, ensure_ascii=False, indent=2)}\n</script>\n'

    # Inject BlogPosting Schema Markup
    meta_desc = data.get("meta_description", "")
    blog_schema = {
        "@context": "https://schema.org",
        "@type": "BlogPosting",
        "headline": h1_title,
        "description": meta_desc,
        "articleSection": data.get("category", "Home & Garden"),
        "keywords": data.get("lsi_keywords", []) + data.get("tags", []),
        "mainEntityOfPage": {"@type": "WebPage"}
    }
    content_html += f'\n<script type="application/ld+json">\n{json.dumps(blog_schema, ensure_ascii=False, indent=2)}\n</script>\n'

    data["content_html"] = content_html
    data["hero_bytes"] = hero_bytes
    return data
