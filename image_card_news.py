"""
Professional Canva / Card-News Style Thumbnail Generator for kgamjablog
Replicates the clean, human-designed Canva layout (reference: media_1790467356308.png):
- Zero AI-diffusion artifacts (100% crisp vector & typographic rendering)
- 100% relevant headline and subtitle matching the exact blog topic
- Pastel background with weekly palette rotation
- Centered white card with bold black outline
- Diagonal red corner ribbon with 'NEW' / '2026' / 'HOT'
- Top coral category/year header (e.g. '2026년 최신판')
- Massive bold yellow headline with solid black outline
- Actionable black subtitle
- 2D counselor character avatar overlapping the bottom border
"""
import os
import sys
import io
import re
import random
from PIL import Image, ImageDraw, ImageFont

# Directory for assets
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

# Pastel background palettes for subtle weekly/thematic diversity
PASTEL_PALETTES = [
    {"bg": (224, 242, 255), "name": "Sky Blue"},     # Default reference pastel blue
    {"bg": (224, 246, 238), "name": "Mint Green"},   # Soft mint
    {"bg": (255, 238, 230), "name": "Warm Peach"},   # Soft peach
    {"bg": (238, 235, 255), "name": "Lavender"},     # Soft lavender
    {"bg": (255, 249, 224), "name": "Sunny Lemon"},  # Soft lemon
    {"bg": (255, 235, 240), "name": "Soft Rose"},    # Soft rose
    {"bg": (226, 248, 250), "name": "Aqua Marine"},  # Soft aqua
]

RIBBON_TEXTS = ["NEW", "2026", "HOT", "필독", "핵심"]

CHARACTER_FILES = [
    "character_counselor_female.png",
    "character_counselor_navy.png",
    "character_counselor_coral.png"
]


def get_system_font(size: int, bold: bool = True):
    """
    Find best bold Korean font across Windows, Ubuntu (GitHub Actions), and local paths.
    """
    candidates = [
        # Local repo font
        os.path.join(BASE_DIR, "fonts", "NanumGothicBold.ttf"),
        os.path.join(BASE_DIR, "fonts", "NanumGothic.ttf"),
        # Ubuntu GitHub Actions font paths
        "/usr/share/fonts/truetype/nanum/NanumGothicBold.ttf",
        "/usr/share/fonts/truetype/nanum/NanumGothic.ttf",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc",
        # Windows font paths
        r"C:\Windows\Fonts\malgunbd.ttf",
        r"C:\Windows\Fonts\malgun.ttf",
        r"C:\Windows\Fonts\NanumGothicBold.ttf",
        r"C:\Windows\Fonts\gulim.ttc"
    ]
    for p in candidates:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                continue
    return ImageFont.load_default()


def extract_headline_and_subtitle(title: str, topic: str = ""):
    """
    Intelligently extracts a punchy main headline (2~4 words) and actionable subtitle.
    Examples:
    - '교통사고 형사합의서 작성법: 처벌불원서 문구 효력과 12대 중과실 예외 기준'
      -> Headline: '교통사고 형사합의서', Subtitle: '처벌불원서 효력과 12대 중과실'
    - '2026년 실업급여 수급조건 및 1일 모의계산'
      -> Headline: '실업급여 수급조건', Subtitle: '2026년 개정 기준 및 1일 모의계산'
    """
    clean = re.sub(r'^[【\[\(][^】\]\)]*[】\]\)]\s*', '', title).strip()
    # Remove leading year if present for headline punch
    year_prefix = ""
    y_m = re.match(r'^(202[0-9]년\s*)', clean)
    if y_m:
        year_prefix = y_m.group(1).strip()
        clean = clean[len(y_m.group(1)):].strip()

    # Split on colon, comma, or dash
    headline = ""
    subtitle = ""

    if ":" in clean:
        parts = clean.split(":", 1)
        headline = parts[0].strip()
        subtitle = parts[1].strip()
    elif " - " in clean:
        parts = clean.split(" - ", 1)
        headline = parts[0].strip()
        subtitle = parts[1].strip()
    elif "?" in clean:
        parts = clean.split("?", 1)
        headline = parts[0].strip() + "?"
        subtitle = parts[1].strip()
    else:
        # Split on conjunctions or spaces
        words = clean.split()
        if len(words) <= 3:
            headline = clean
            subtitle = "가입요령, 회사별비교" if "보험" in clean else "핵심 요건과 실무 절차 총정리"
        else:
            headline = " ".join(words[:2])
            subtitle = " ".join(words[2:])

    # Clean subtitle length
    if len(subtitle) > 22:
        subtitle = subtitle[:20].rstrip(',·- ') + "..."

    # If headline is still too long (> 12 chars), shorten
    if len(headline) > 12:
        h_words = headline.split()
        if len(h_words) >= 2:
            headline = " ".join(h_words[:2])

    if not subtitle:
        subtitle = "핵심 요건 및 실무 절차 완벽정리"

    return headline, subtitle


def generate_card_news_image(
    title: str,
    category: str = "",
    top_label: str = "2026년 최신판",
    ribbon_text: str = None,
    palette_index: int = None
) -> bytes:
    """
    Renders the exact Canva card-news reference layout (800x800).
    Returns JPEG bytes.
    """
    W, H = 800, 800

    # Choose background palette
    if palette_index is not None:
        palette = PASTEL_PALETTES[palette_index % len(PASTEL_PALETTES)]
    else:
        # Deterministic based on title hash so it's consistent for the same title
        h_val = sum(ord(c) for c in title)
        palette = PASTEL_PALETTES[h_val % len(PASTEL_PALETTES)]

    bg_color = palette["bg"]
    img = Image.new("RGB", (W, H), bg_color)
    draw = ImageDraw.Draw(img)

    # White card coordinates (proportional to reference)
    card_x1 = 110
    card_x2 = 690
    card_y1 = 110
    card_y2 = 640
    border_width = 5

    # Draw centered white card
    draw.rectangle(
        [(card_x1, card_y1), (card_x2, card_y2)],
        fill=(255, 255, 255),
        outline=(0, 0, 0),
        width=border_width
    )

    # Red diagonal ribbon on top-left corner
    ribbon_triangle = [
        (card_x1 + border_width // 2, card_y1 + border_width // 2),
        (card_x1 + 140, card_y1 + border_width // 2),
        (card_x1 + border_width // 2, card_y1 + 140)
    ]
    draw.polygon(ribbon_triangle, fill=(235, 10, 10))

    # Ribbon text (rotated 45 deg)
    ribbon_txt = ribbon_text or "NEW"
    f_ribbon = get_system_font(28)
    txt_img = Image.new("RGBA", (160, 160), (0, 0, 0, 0))
    txt_draw = ImageDraw.Draw(txt_img)
    txt_draw.text((40, 40), ribbon_txt, font=f_ribbon, fill=(255, 255, 255))
    rotated_txt = txt_img.rotate(45, resample=Image.Resampling.BICUBIC)
    img.paste(rotated_txt, (card_x1 - 10, card_y1 - 10), rotated_txt)

    # Extract headline & subtitle
    main_text, sub_text = extract_headline_and_subtitle(title)

    # Top coral label (e.g. '2026년 최신판')
    f_top = get_system_font(40)
    bbox_top = draw.textbbox((0, 0), top_label, font=f_top)
    tw_top = bbox_top[2] - bbox_top[0]
    draw.text(((W - tw_top) // 2, card_y1 + 45), top_label, font=f_top, fill=(235, 60, 40))

    # Dynamic main headline sizing based on text length
    if len(main_text) <= 4:
        main_font_size = 84
        stroke_w = 8
    elif len(main_text) <= 6:
        main_font_size = 76
        stroke_w = 7
    elif len(main_text) <= 8:
        main_font_size = 66
        stroke_w = 6
    else:
        main_font_size = 56
        stroke_w = 5

    f_main = get_system_font(main_font_size)
    bbox_m = draw.textbbox((0, 0), main_text, font=f_main)
    tw_m = bbox_m[2] - bbox_m[0]
    th_m = bbox_m[3] - bbox_m[1]
    tx_m = (W - tw_m) // 2
    ty_m = card_y1 + 115

    # Yellow fill with thick black stroke
    draw.text(
        (tx_m, ty_m),
        main_text,
        font=f_main,
        fill=(255, 235, 0),
        stroke_width=stroke_w,
        stroke_fill=(0, 0, 0)
    )

    # Subtitle text with automatic scaling to ensure wide margins
    max_sub_w = (card_x2 - card_x1) - 60
    sub_font_size = 40
    f_sub = get_system_font(sub_font_size)
    bbox_s = draw.textbbox((0, 0), sub_text, font=f_sub)
    tw_s = bbox_s[2] - bbox_s[0]

    while tw_s > max_sub_w and sub_font_size > 24:
        sub_font_size -= 2
        f_sub = get_system_font(sub_font_size)
        bbox_s = draw.textbbox((0, 0), sub_text, font=f_sub)
        tw_s = bbox_s[2] - bbox_s[0]

    draw.text(((W - tw_s) // 2, ty_m + th_m + 45), sub_text, font=f_sub, fill=(0, 0, 0))

    # Paste 2D character at bottom overlapping card border
    # Pick character variant
    char_filename = CHARACTER_FILES[0]
    h_char = sum(ord(c) for c in (category or title))
    char_candidate = os.path.join(ASSETS_DIR, CHARACTER_FILES[h_char % len(CHARACTER_FILES)])
    if os.path.exists(char_candidate):
        char_path = char_candidate
    else:
        char_path = os.path.join(ASSETS_DIR, "character_counselor_female.png")

    if os.path.exists(char_path):
        try:
            char = Image.open(char_path).convert("RGBA")
            char_w = 420
            char_h = int(char.height * (char_w / char.width))
            char_resized = char.resize((char_w, char_h), Image.Resampling.LANCZOS)
            char_x = (W - char_w) // 2 + 10
            char_y = H - char_h
            img.paste(char_resized, (char_x, char_y), char_resized)
        except Exception as e:
            print(f"⚠️ [CardNews] Character overlay error: {e}")

    # Output JPEG bytes
    out_buf = io.BytesIO()
    img.save(out_buf, format="JPEG", quality=95)
    return out_buf.getvalue()
