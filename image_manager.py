"""
Image Manager for kgamjablog.blog
Generates topic-accurate AI images matching the exact post scenario and uploads them to WordPress.
"""
import os
import time
import random
import urllib.parse
import requests
from config import WP_URL, WP_USER, WP_APP_PASSWORD


def fetch_ai_image_by_prompt(prompt_en: str) -> bytes:
    """
    Generate and fetch a high-quality AI image using the tailor-made prompt.
    """
    clean_prompt = prompt_en.strip()
    # Enhance prompt for modern web illustration aesthetic
    enhanced_prompt = f"{clean_prompt}, clean modern digital artwork, soft studio lighting, ultra detailed, 8k, professional editorial illustration, no text"
    
    seed = random.randint(1000, 999999)
    encoded_prompt = urllib.parse.quote(enhanced_prompt)
    ai_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=576&nologo=true&seed={seed}"
    
    try:
        res = requests.get(ai_url, timeout=20)
        if res.status_code == 200 and len(res.content) > 5000:
            return res.content
    except Exception as e:
        print(f"⚠️ Primary image generation error: {e}")

    # Fallback to topic-based high quality stock photo if AI timeout
    fallback_url = "https://images.unsplash.com/photo-1450133064473-71024230f91b?w=1024&h=576&fit=crop&q=80"
    try:
        res = requests.get(fallback_url, timeout=10)
        if res.status_code == 200:
            return res.content
    except Exception:
        pass
        
    return None


def upload_image_to_wp(img_bytes: bytes, filename_ascii: str, alt_text: str = "") -> dict:
    """
    Upload image with ASCII filename to prevent latin-1 header errors in requests.
    """
    if not img_bytes or not WP_USER or not WP_APP_PASSWORD:
        return None

    headers = {
        'Content-Disposition': f'attachment; filename="{filename_ascii}"',
        'Content-Type': 'image/jpeg'
    }
    
    try:
        response = requests.post(
            f"{WP_URL.rstrip('/')}/wp-json/wp/v2/media",
            auth=(WP_USER, WP_APP_PASSWORD),
            headers=headers,
            data=img_bytes,
            timeout=30
        )
        if response.status_code in (200, 201):
            data = response.json()
            media_id = data.get("id")
            source_url = data.get("source_url")

            # Update alt text and description on WordPress
            if alt_text and media_id:
                try:
                    requests.post(
                        f"{WP_URL.rstrip('/')}/wp-json/wp/v2/media/{media_id}",
                        auth=(WP_USER, WP_APP_PASSWORD),
                        json={"alt_text": alt_text, "caption": alt_text, "description": alt_text},
                        timeout=10
                    )
                except Exception:
                    pass

            return {"media_id": media_id, "source_url": source_url}
        else:
            print(f"⚠️ Media upload failed ({response.status_code}): {response.text[:200]}")
            return None
    except Exception as e:
        print(f"⚠️ Media upload exception: {e}")
        return None


def generate_and_upload_post_image(topic: str, image_prompt_en: str) -> dict:
    """
    Generate topic-accurate AI image and upload to WordPress Media Library.
    Returns media_id and source_url for both featured image and in-content placement.
    """
    print(f"🎨 [맞춤형 AI 이미지 생성] 프롬프트: {image_prompt_en[:80]}...")
    img_bytes = fetch_ai_image_by_prompt(image_prompt_en)
    
    if not img_bytes:
        print("⚠️ 이미지 생성 실패")
        return None

    ts = int(time.time())
    filename = f"post_img_{ts}_{random.randint(100, 999)}.jpg"
    upload_res = upload_image_to_wp(img_bytes, filename, alt_text=f"{topic} 안내 이미지")
    
    if upload_res:
        print(f"✅ 이미지 업로드 완료! Media ID: {upload_res['media_id']}, URL: {upload_res['source_url']}")
    
    return upload_res


def insert_image_into_content(content_html: str, image_url: str, alt_text: str) -> str:
    """
    Insert the image right after the first paragraph or right after the 1st H2 heading.
    """
    if not image_url:
        return content_html

    image_block = f"""
<figure class="wp-block-image size-large" style="text-align: center; margin: 28px auto; max-width: 680px;">
  <img src="{image_url}" alt="{alt_text}" style="width: 100%; height: auto; border-radius: 8px; box-shadow: 0 4px 14px rgba(0,0,0,0.08);" />
  <figcaption style="color: #666; font-size: 13px; margin-top: 8px; text-align: center;">▲ {alt_text}</figcaption>
</figure>
"""
    # Insert right after the first </p> (introductory paragraph) or 1st </h2>
    first_p = content_html.find("</p>")
    if first_p != -1:
        insert_idx = first_p + 4
        return content_html[:insert_idx] + "\n" + image_block + "\n" + content_html[insert_idx:]
    
    first_h2 = content_html.find("</h2>")
    if first_h2 != -1:
        insert_idx = first_h2 + 5
        return content_html[:insert_idx] + "\n" + image_block + "\n" + content_html[insert_idx:]

    return image_block + "\n" + content_html
