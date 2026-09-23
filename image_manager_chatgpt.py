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
        r"C:\Windows\Fonts\YuGothB.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        r"C:\Windows\Fonts\msgothic.ttc",
        "fonts/NotoSansJP-Variable.ttf",
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

        # Crop bottom 65px to eliminate any third-party diffusion watermark
        if h > 300:
            img = img.crop((0, 0, w, max(100, h - 65))).resize((w, h), Image.Resampling.LANCZOS)

        overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)

        # Clean title prefix like 【体験談】, [실전후기]
        clean_title = re.sub(r'^[【\[\(][^】\]\)]*[】\]\)]\s*', '', title).strip()
        if not clean_title:
            clean_title = title.strip()

        # Standardize fullwidth punctuation for precise hook extraction
        t_split = clean_title.replace('！', '!').replace('？', '?').replace('：', ':')
        if "?" in t_split:
            main_text = clean_title[:t_split.index("?") + 1].strip()
        elif "!" in t_split:
            main_text = clean_title[:t_split.index("!") + 1].strip()
        elif ":" in t_split:
            main_text = clean_title[:t_split.index(":")].strip()
        elif "," in t_split and 8 <= t_split.index(",") <= 24:
            main_text = clean_title[:t_split.index(",")].strip()
        else:
            main_text = clean_title[:24].strip()
        main_text = main_text.rstrip(',-·: ')

        # Load bold fonts
        if language == "ja":
            font_title = get_japanese_font(36 if len(main_text) <= 16 else (30 if len(main_text) <= 22 else 26))
            font_badge = get_japanese_font(18)
            badge_category = category if category else "暮らしの法律"
            badge_color = (13, 148, 136, 255) # Teal
        else:
            font_title = get_korean_font(38 if len(main_text) <= 16 else (32 if len(main_text) <= 22 else 26))
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


def fetch_cartoon_render_from_flux(title: str, category: str = None) -> bytes:
    """
    Generate a pristine, text-free 2D modern Korean cartoon / webtoon comic scene using diffusion.
    STRICTLY avoids passing non-English text or requesting text generation to prevent corrupted glyphs.
    """
    combined = f"{title} {category or ''}".lower()

    if any(k in combined for k in ["보이스피싱", "사기", "추심", "스팸", "지급정지", "해킹"]):
        scene = "determined Korean character holding glowing golden shield blocking phone scam, cyber financial protection in comic style"
    elif any(k in combined for k in ["택배", "배달", "이물질", "환불", "중고", "직거래", "소비자", "피해"]):
        scene = "relatable Korean consumer successfully receiving full refund for delivered package, smiling with relief in comic style"
    elif any(k in combined for k in ["부동산", "전세", "월세", "임대", "등기부", "이사", "아파트", "계약서"]):
        scene = "cheerful young Korean tenant holding house keys and apartment lease contract document, cozy sunny apartment in comic style"
    elif any(k in combined for k in ["퇴직금", "임금", "급여", "근로", "알바", "휴직", "노동청", "주휴"]):
        scene = "joyful Korean office worker cheering with paycheck envelope and bank passbook, bright office desk in comic style"
    elif any(k in combined for k in ["연금", "상속", "세금", "증여", "적금", "대출", "금리", "리볼빙", "신용", "가산세"]):
        scene = "smart Korean professional calculating financial savings with calculator and bankbook, stacks of golden coins in comic style"
    elif any(k in combined for k in ["소송", "합의", "법률", "판결", "내용증명", "교통사고", "과태료"]):
        scene = "confident Korean citizen holding signed legal agreement document, golden scales of justice in friendly law office in comic style"
    else:
        scene = "friendly smart Korean person giving helpful guidance thumbs-up, bright desk with useful guides and documents in comic style"

    prompt = (
        f"2D modern Korean webtoon comic illustration, {scene}, "
        f"clean crisp black outline drawing, charming relatable Korean character, "
        f"vibrant flat pastel colors, modern Korean instatoon manhwa comic art, clear cel shading, "
        f"bright cheerful lighting, strictly 2D flat illustration, no 3D rendering, no CGI, no photorealism, no text"
    )

    encoded = urllib.parse.quote(prompt)
    print(f"[2D Cartoon Engine] Generating 2D comic illustration: {prompt[:70]}...")

    configs = [
        {"model": "flux", "timeout": 45},
        {"model": None, "timeout": 30},
        {"model": None, "timeout": 30}
    ]

    for attempt, cfg in enumerate(configs, 1):
        seed = random.randint(1000, 999999)
        m = f"model={cfg['model']}&" if cfg["model"] else ""
        url = f"https://image.pollinations.ai/prompt/{encoded}?{m}width=1024&height=576&nologo=true&seed={seed}"

        try:
            res = requests.get(url, timeout=cfg["timeout"])
            if res.status_code == 200 and len(res.content) > 5000:
                print(f"✅ [2D Cartoon Engine] 2D 카툰 일러스트 다운로드 완료 ({len(res.content)} bytes, attempt {attempt})")
                return res.content
        except Exception as e:
            print(f"⚠️ [2D Cartoon Engine] Attempt {attempt} error: {e}")

    try:
        backup = requests.get("https://images.unsplash.com/photo-1579546929518-9e396f3cc809?w=1024&h=576&fit=crop&q=80", timeout=15)
        if backup.status_code == 200:
            return backup.content
    except Exception:
        pass
    return None


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
    Generate card-news thumbnail for blog posts:
    - Korean blog (language='ko'): 2D Korean webtoon cartoon illustration + HD typography overlay.
    - Japanese blog (language='ja'): 3D Pixar character scene + HD typography overlay.
    """
    if language == "ko":
        print("[KR Cartoon Thumbnail] Generating 2D Korean webtoon cartoon thumbnail...")
        raw_cartoon_bytes = fetch_cartoon_render_from_flux(title, category=category)
        if raw_cartoon_bytes:
            final_thumb = apply_card_news_typography_overlay(raw_cartoon_bytes, title, category=category, language="ko")
            return final_thumb
        return None

    api_key = os.environ.get("OPENAI_API_KEY")

    prompt = (
        f"「{title}」\n"
        f"このタイトルに合うブログサムネイル画像を作成してください。"
        f"YouTubeカードニューススタイル、鮮明で太い日本語テキストタイポグラフィ、"
        f"可愛い3Dキャラクター（ピクサー風）、関連する3D金融・法律アイコン、明るく清潔なスタジオ照明、高画質3Dレンダリング。"
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
                    print(f"⚠️ [ChatGPT Image] OpenAI API 429: 크레딧 잔액 부족 ($0).")
                    break
                else:
                    print(f"⚠️ [ChatGPT Image] {model} status {res.status_code}: {res.text[:120]}")
            except Exception as e:
                print(f"⚠️ [ChatGPT Image] Error: {e}")

    # Fallback for JP: Clean 3D Pixar render + Crisp Typography Overlay
    print("[ChatGPT Image Fallback] Using Fail-Safe 3D Scene + HD Card-News Typography Overlay...")
    raw_3d_bytes = fetch_3d_render_from_flux(title, category=category, language=language)
    if raw_3d_bytes:
        final_thumb = apply_card_news_typography_overlay(raw_3d_bytes, title, category=category, language=language)
        return final_thumb

    return None


def fetch_cartoon_thumbnail_bytes(title: str, category: str = None) -> bytes:
    """
    Explicit helper to generate 2D Korean cartoon card-news thumbnail bytes.
    """
    return fetch_chatgpt_thumbnail_bytes(title, language="ko", category=category)

