"""
ChatGPT (OpenAI) Image Generator for Korean and Japanese Blog Thumbnails
Produces 3D Card-News / YouTube Thumbnail Style Art matching the user reference:
- Cute 3D character (Pixar/Disney aesthetic)
- Bold, highly legible Korean / Japanese text typography
- Topic-specific 3D objects and financial/legal icons
- Clean, bright 3D studio lighting
"""
import os
import sys
import requests
from image_manager_flux import fetch_flux_image_bytes

try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass


def fetch_chatgpt_thumbnail_bytes(title: str, language: str = "ko") -> bytes:
    """
    Generate ChatGPT (OpenAI) style 3D card-news thumbnail for blog posts.
    Uses OpenAI Images API (chatgpt-image-latest / gpt-image-1) with the user's prompt format.
    Gracefully falls back if OpenAI API key is missing or credit exhausted.
    """
    api_key = os.environ.get("OPENAI_API_KEY")
    
    if language == "ja":
        prompt = (
            f"「{title}」\n"
            f"このタイトルに合うブログサムネイル画像を作成してください。"
            f"YouTubeカードニューススタイル、鮮明で太い日本語テキストタイポグラフィ、"
            f"可愛い3Dキャラクター（ピクサー風）、関連する3D金融・法律アイコン、明るく清潔なスタジオ照明、高画質3Dレンダリング。"
        )
    else:
        prompt = (
            f"{title}\n"
            f"이 제목과 어울리는 블로그 썸네일 이미지 만들어줘."
            f"유튜브 카드뉴스 썸네일 스타일, 선명하고 굵은 한글 텍스트 타이포그래피, "
            f"귀여운 3D 캐릭터(픽사/디즈니 스타일), 주제와 어울리는 3D 금융/법률 아이콘 오브젝트, 화사하고 깔끔한 3D 스튜디오 조명."
        )

    if api_key:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        models_to_try = ["chatgpt-image-latest", "gpt-image-1", "gpt-image-1-mini", "gpt-image-2"]
        for model in models_to_try:
            try:
                print(f"[ChatGPT Image] Requesting 3D thumbnail via OpenAI ({model})...")
                payload = {
                    "model": model,
                    "prompt": prompt,
                    "n": 1,
                    "size": "1024x1024"
                }
                res = requests.post("https://api.openai.com/v1/images/generations", headers=headers, json=payload, timeout=60)
                if res.status_code == 200:
                    img_url = res.json()["data"][0]["url"]
                    img_res = requests.get(img_url, timeout=30)
                    if img_res.status_code == 200 and len(img_res.content) > 5000:
                        print(f"🎉 [ChatGPT Image] Successfully generated 3D thumbnail via OpenAI ({len(img_res.content)} bytes)!")
                        return img_res.content
                elif res.status_code == 429:
                    print(f"⚠️ [ChatGPT Image] OpenAI API 429: 크레딧 잔액 부족 (https://platform.openai.com/ 충전 필요)")
                    break
                else:
                    print(f"⚠️ [ChatGPT Image] {model} status {res.status_code}")
            except Exception as e:
                print(f"⚠️ [ChatGPT Image] Error: {e}")

    # Fallback to enhanced 3D prompt with FLUX engine
    print("[ChatGPT Image Fallback] Using enhanced 3D card-news prompt via fallback engine...")
    fallback_prompt = (
        f"Korean YouTube thumbnail card news style, {title}, cute 3D character, "
        f"piggy bank, coins, calendar, shield, bold typography text overlay, vibrant 3D Pixar render, clean soft studio lighting"
    )
    return fetch_flux_image_bytes(fallback_prompt)
