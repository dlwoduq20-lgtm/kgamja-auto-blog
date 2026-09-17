"""
ChatGPT (OpenAI) Image Generator & 3D Card-News Fallback Generator
for Korean (kgamjablog) and Japanese (seikatsulaw) Blogs.

Produces YouTube Card-News 3D Thumbnails:
1. Primary: Official OpenAI Image API (chatgpt-image-latest / gpt-image-1) when API credits are active.
2. Fallback: Clean 3D Pixar character render + Pillow (PIL) high-contrast bold typography overlay.
   - Strictly NO diffusion text generation (prevents alien/corrupted glyphs).
   - Razor-sharp, 100% human-readable Korean / Japanese card-news typography.
"""
import os
import sys
import io
import re
import random
import urllib.parse
import requests
from PIL import Image, ImageDraw, ImageFont

try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass


def get_korean_font(size: int):
    candidates = [
        "fonts/NanumGothicBold.ttf",
        "/usr/share/fonts/truetype/nanum/NanumGothicBold.ttf",
        "/usr/share/fonts/truetype/nanum/NanumGothic.ttf",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
        r"C:\Windows\Fonts\malgunbd.ttf",
        r"C:\Windows\Fonts\malgun.ttf",
        r"C:\Windows\Fonts\gulim.ttc"
    ]
    for p in candidates:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                continue
    return ImageFont.load_default()


def get_japanese_font(size: int):
    candidates = [
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "fonts/NotoSansJP-Variable.ttf",
        r"C:\Windows\Fonts\YuGothB.ttc",
        r"C:\Windows\Fonts\msgothic.ttc",
        "fonts/NanumGothicBold.ttf"
    ]
    for p in candidates:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                continue
    return ImageFont.load_default()


def apply_card_news_typography_overlay(
    image_bytes: bytes,
    title: str,
    category: str = None,
    language: str = "ko"
) -> bytes:
    """
    Overlays a sleek, professional YouTube card-news banner onto the 3D render.
    Ensures 100% crystal-clear, bold typography with zero distortion.
    """
    try:
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        w, h = img.size

        # Crop bottom 35px to eliminate any third-party diffusion watermark
        if h > 300:
            img = img.crop((0, 0, w, h - 35)).resize((w, h), Image.Resampling.LANCZOS)

        overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)

        # Extract punchy main question or statement
        clean_title = title.strip()
        if "?" in clean_title:
            main_text = clean_title.split("?")[0].strip() + "?"
        elif "!" in clean_title:
            main_text = clean_title.split("!")[0].strip() + "!"
        elif ":" in clean_title:
            main_text = clean_title.split(":")[0].strip()
        else:
            main_text = clean_title[:24].strip()

        # Load bold fonts
        if language == "ja":
            font_title = get_japanese_font(36 if len(main_text) <= 16 else 30)
            font_badge = get_japanese_font(18)
            badge_category = category if category else "暮らしの法律"
            badge_color = (13, 148, 136, 255) # Teal
        else:
            font_title = get_korean_font(38 if len(main_text) <= 18 else 32)
            font_badge = get_korean_font(18)
            badge_category = category if category else "생활법률"
            badge_color = (234, 88, 12, 255) # Amber Orange

        # Banner Dimensions (24% of image height)
        banner_h = int(h * 0.25)

        # Dark modern navy banner background
        draw.rectangle([(0, 0), (w, banner_h)], fill=(15, 23, 42, 238))
        # Vibrant gold/yellow accent separator line
        draw.line([(0, banner_h), (w, banner_h)], fill=(250, 204, 21, 255), width=5)

        # Category Pill Badge
        badge_text = f" {badge_category} "
        bbox_b = draw.textbbox((0, 0), badge_text, font=font_badge)
        bw = bbox_b[2] - bbox_b[0] + 16
        bh = bbox_b[3] - bbox_b[1] + 8
        badge_x = (w - bw) // 2
        badge_y = 14
        draw.rounded_rectangle([(badge_x, badge_y), (badge_x + bw, badge_y + bh)], radius=6, fill=badge_color)
        draw.text((badge_x + 8, badge_y + 2), badge_text, font=font_badge, fill=(255, 255, 255, 255))

        # Main Headline Text (Centered with drop shadow)
        bbox_t = draw.textbbox((0, 0), main_text, font=font_title)
        tw = bbox_t[2] - bbox_t[0]
        th = bbox_t[3] - bbox_t[1]
        tx = (w - tw) // 2
        ty = badge_y + bh + 12

        # Draw dark shadow behind text for maximum legibility
        draw.text((tx + 2, ty + 2), main_text, font=font_title, fill=(0, 0, 0, 220))
        draw.text((tx, ty), main_text, font=font_title, fill=(255, 255, 255, 255))

        # Composite overlay
        final_img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
        out_buf = io.BytesIO()
        final_img.save(out_buf, format="JPEG", quality=95)
        return out_buf.getvalue()

    except Exception as e:
        print(f"⚠️ [Typography Overlay Error] {e}. Using raw image.")
        return image_bytes


def fetch_3d_render_from_flux(title: str, category: str = None, language: str = "ko") -> bytes:
    """
    Generate a pristine, text-free 3D Pixar/Disney style scene using FLUX diffusion.
    STRICTLY avoids passing non-English text or requesting text generation to prevent corrupted glyphs.
    """
    # Detect visual thematic props from keywords
    title_lower = (title + " " + (category or "")).lower()
    
    if any(k in title_lower for k in ["부동산", "전세", "월세", "아파트", "주택", "임대", "賃貸", "不動産", "家"]):
        visual_props = "miniature modern suburban house model, golden home keys, rental contract deed, city skyline"
    elif any(k in title_lower for k in ["세금", "상속", "증여", "연금", "적금", "가산세", "절세", "相続", "税金", "遺産", "年金"]):
        visual_props = "cute piggy bank, stacks of gold coins, calculator, tax paper documents, glowing golden shield"
    elif any(k in title_lower for k in ["퇴직금", "임금", "근로", "알바", "실업급여", "노동", "給与", "労働", "退職"]):
        visual_props = "modern slim laptop, monthly paycheck, hourglass, office workspace, financial growth chart"
    elif any(k in title_lower for k in ["법률", "소송", "계약", "합의", "피해", "사기", "재판", "法律", "裁判", "トラブル"]):
        visual_props = "golden scales of justice, wooden judge gavel, official signed contract, glowing shield of protection"
    else:
        visual_props = "cute piggy bank, stacks of shiny coins, office calculator, documents, glowing shield"

    character = "Korean young professional woman smiling warmly" if language == "ko" else "Japanese young professional woman smiling warmly"

    prompt = (
        f"Cute 3D Pixar Disney style character, {character} sitting at a bright modern desk, "
        f"{visual_props}, bright warm 3D studio lighting, soft shadows, vibrant cheerful colors, "
        f"high detail octane 3D digital art, strictly no text, no letters, no words, no numbers, no typography, clean background"
    )

    encoded = urllib.parse.quote(prompt)
    print(f"[3D Fallback Engine] Generating textless 3D render ({visual_props[:40]}...)...")

    configs = [
        {"model": "flux", "timeout": 45},
        {"model": None, "timeout": 40},
        {"model": None, "timeout": 40}
    ]

    for attempt, cfg in enumerate(configs, 1):
        seed = random.randint(1000, 999999)
        if cfg["model"]:
            url = f"https://image.pollinations.ai/prompt/{encoded}?model={cfg['model']}&width=1024&height=576&nologo=true&seed={seed}"
        else:
            url = f"https://image.pollinations.ai/prompt/{encoded}?width=1024&height=576&nologo=true&seed={seed}"

        try:
            res = requests.get(url, timeout=cfg["timeout"])
            if res.status_code == 200 and len(res.content) > 5000:
                print(f"✅ [3D Fallback Engine] 3D 렌더링 다운로드 완료 ({len(res.content)} bytes, attempt {attempt})")
                return res.content
        except Exception as e:
            print(f"⚠️ [3D Fallback Engine] Attempt {attempt} error: {e}")

    # Ultimate backup fallback
    try:
        backup = requests.get("https://images.unsplash.com/photo-1554224155-8d04cb21cd6c?w=1024&h=576&fit=crop&q=80", timeout=15)
        if backup.status_code == 200:
            return backup.content
    except Exception:
        pass
    return None


def fetch_chatgpt_thumbnail_bytes(title: str, language: str = "ko", category: str = None) -> bytes:
    """
    Generate ChatGPT (OpenAI) style 3D card-news thumbnail for blog posts.
    
    Workflow:
    1. Attempts OpenAI Image API (chatgpt-image-latest / gpt-image-1) using the user's prompt template.
    2. If OpenAI has no credits (429) or is unavailable:
       Falls back to generating a clean, textless 3D Pixar render and applying a crystal-clear,
       bold Korean/Japanese typography banner via Pillow (PIL). Zero distorted characters guaranteed.
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
        models_to_try = ["chatgpt-image-latest", "gpt-image-1", "gpt-image-1-mini", "gpt-image-1.5"]
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
                    print(f"⚠️ [ChatGPT Image] OpenAI API 429: 크레딧 잔액 부족 ($0). platform.openai.com/settings/organization/billing 에서 충전 시 공식 ChatGPT 이미지 모델이 사용됩니다.")
                    break
                else:
                    print(f"⚠️ [ChatGPT Image] {model} status {res.status_code}: {res.text[:120]}")
            except Exception as e:
                print(f"⚠️ [ChatGPT Image] Error: {e}")

    # Fallback: Clean 3D Pixar render + Crisp Typography Overlay
    print("[ChatGPT Image Fallback] Using Fail-Safe 3D Pixar Scene + HD Card-News Typography Overlay...")
    raw_3d_bytes = fetch_3d_render_from_flux(title, category=category, language=language)
    if raw_3d_bytes:
        final_thumb = apply_card_news_typography_overlay(raw_3d_bytes, title, category=category, language=language)
        return final_thumb

    return None
