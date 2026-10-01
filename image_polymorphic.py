"""
Polymorphic Multi-Layout Thumbnail Generator for kgamjablog & Global Blogs.
Eliminates repetitive AI aesthetics by supporting 5 completely distinct visual layouts:

Layout 1: [Editorial Minimal] - Dark Charcoal/Navy background + Elegant Typography + Minimal Accent Bar (Brunch/WSJ Style)
Layout 2: [Document & Rubber Stamp] - Manila Folder/Paper background + Post-it Notes + Tilted Red Stamp ("반려주의", "필수확인", "2026개정")
Layout 3: [Fintech Stat / Metrics] - Vibrant Gradient + Giant Central Metric ("최대 5억원", "100% 반환", "3단계") + Modern Badges
Layout 4: [Photo Duotone & Title Bar] - Curated photographic backdrop + Deep duotone color wash + Editorial Headline
Layout 5: [Card News 2.0] - Modernized Canva-style Card News (Rotating colors & dynamic geometry)
"""
import os
import sys
import io
import re
import math
import random
import requests
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FONTS_DIR = os.path.join(BASE_DIR, "fonts")
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

W, H = 800, 800


def get_font(size: int, bold: bool = True):
    candidates = [
        os.path.join(FONTS_DIR, "NanumGothicBold.ttf"),
        os.path.join(FONTS_DIR, "NanumGothic.ttf"),
        "/usr/share/fonts/truetype/nanum/NanumGothicBold.ttf",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
        r"C:\Windows\Fonts\malgunbd.ttf",
        r"C:\Windows\Fonts\malgun.ttf",
        r"C:\Windows\Fonts\NanumGothicBold.ttf"
    ]
    for p in candidates:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                continue
    return ImageFont.load_default()


def clean_title_for_display(title: str):
    clean = re.sub(r'^[【\[\(][^】\]\)]*[】\]\)]\s*', '', title).strip()
    return clean


def split_headline_smart(title: str):
    clean = clean_title_for_display(title)
    # Check delimiters
    for sep in [":", " - ", "?", " | "]:
        if sep in clean:
            parts = clean.split(sep, 1)
            h = parts[0].strip()
            s = parts[1].strip()
            if sep == "?":
                h += "?"
            return h, s

    words = clean.split()
    if len(words) <= 3:
        return clean, "핵심 쟁점 및 실무 가이드"
    return " ".join(words[:2]), " ".join(words[2:])


# ==============================================================================
# LAYOUT 1: [Editorial Minimal] - WSJ / Brunch / Longform Journalism Style
# ==============================================================================
def render_editorial_minimal(title: str, category: str = "생활법률") -> bytes:
    img = Image.new("RGB", (W, H), (15, 23, 42)) # Deep Slate Navy
    draw = ImageDraw.Draw(img)

    # Subtle background accent lines
    for i in range(0, W, 80):
        draw.line([(i, 0), (i, H)], fill=(22, 33, 60), width=1)

    # Accent color box / header
    draw.rectangle([(60, 60), (W - 60, H - 60)], outline=(30, 41, 59), width=2)
    
    # Top Tag
    f_tag = get_font(22)
    tag_text = f"SPECIAL REPORT  |  {category.upper() if category else 'LEGAL & FINANCE'}"
    draw.text((80, 80), tag_text, font=f_tag, fill=(56, 189, 248)) # Sky blue

    # Gold accent divider line
    draw.line([(80, 120), (180, 120)], fill=(245, 158, 11), width=4) # Amber

    # Headline
    headline, subtitle = split_headline_smart(title)
    
    # Wrap headline if needed
    f_title = get_font(52)
    lines = []
    if len(headline) > 12:
        words = headline.split()
        if len(words) >= 2:
            lines = [" ".join(words[:len(words)//2]), " ".join(words[len(words)//2:])]
        else:
            lines = [headline[:10], headline[10:]]
    else:
        lines = [headline]

    y = 220
    for line in lines:
        draw.text((80, y), line, font=f_title, fill=(255, 255, 255))
        y += 75

    # Subtitle
    if subtitle:
        y += 20
        # Draw accent left border for subtitle
        draw.line([(80, y), (80, y + 80)], fill=(56, 189, 248), width=4)
        f_sub = get_font(28)
        # Wrap subtitle to max 22 chars
        sub_wrapped = subtitle if len(subtitle) <= 22 else subtitle[:20] + "..."
        draw.text((100, y + 10), sub_wrapped, font=f_sub, fill=(203, 213, 225))
        f_sub_detail = get_font(20)
        draw.text((100, y + 50), "실무 절차 · 분쟁 예방 체크포인트 완벽 정리", font=f_sub_detail, fill=(148, 163, 184))

    # Bottom footer branding
    draw.line([(80, H - 120), (W - 80, H - 120)], fill=(30, 41, 59), width=1)
    f_foot = get_font(18)
    draw.text((80, H - 100), "생활 속 법과 금융  |  2026 OFFICIAL GUIDE", font=f_foot, fill=(100, 116, 139))
    draw.text((W - 220, H - 100), "VERIFIED CONTENT", font=f_foot, fill=(34, 197, 94))

    out_buf = io.BytesIO()
    img.save(out_buf, format="JPEG", quality=95)
    return out_buf.getvalue()


# ==============================================================================
# LAYOUT 2: [Document & Rubber Stamp] - Real Official Paper / Folder Style
# ==============================================================================
def render_document_stamp(title: str, category: str = "행정실무") -> bytes:
    # Cream / Manila document background
    img = Image.new("RGB", (W, H), (246, 241, 230))
    draw = ImageDraw.Draw(img)

    # Document border
    draw.rectangle([(50, 50), (W - 50, H - 50)], fill=(255, 255, 255), outline=(214, 205, 190), width=3)
    # Subtle drop shadow lines
    draw.rectangle([(55, 55), (W - 45, H - 45)], outline=(229, 223, 210), width=2)

    # Folder Tab on Top
    draw.polygon([(80, 50), (260, 50), (240, 20), (100, 20)], fill=(230, 215, 195))
    f_tab = get_font(16)
    draw.text((115, 26), "CASE FILE #2026", font=f_tab, fill=(120, 100, 80))

    # Document Header
    f_doc_title = get_font(22)
    draw.text((90, 85), f"[실무 사건 검토 보고서]  카테고리: {category}", font=f_doc_title, fill=(100, 90, 80))
    draw.line([(90, 120), (W - 90, 120)], fill=(180, 170, 160), width=2)

    headline, subtitle = split_headline_smart(title)

    # Main Headline
    f_h = get_font(46)
    # Wrap headline
    h_words = headline.split()
    if len(headline) > 13 and len(h_words) >= 2:
        h1 = " ".join(h_words[:len(h_words)//2])
        h2 = " ".join(h_words[len(h_words)//2:])
        draw.text((90, 150), h1, font=f_h, fill=(20, 20, 20))
        draw.text((90, 210), h2, font=f_h, fill=(20, 20, 20))
        y_next = 290
    else:
        draw.text((90, 165), headline, font=f_h, fill=(20, 20, 20))
        y_next = 245

    draw.line([(90, y_next), (W - 90, y_next)], fill=(220, 215, 205), width=1)

    # Yellow Sticky Post-it Note
    postit_x = 90
    postit_y = y_next + 30
    postit_w = 400
    postit_h = 240
    draw.rectangle([(postit_x, postit_y), (postit_x + postit_w, postit_y + postit_h)], fill=(254, 240, 138), outline=(250, 204, 21), width=2)
    
    # Tape at top of post-it
    draw.rectangle([(postit_x + 130, postit_y - 10), (postit_x + 270, postit_y + 10)], fill=(255, 255, 255, 180), outline=(230, 230, 230))

    f_p_title = get_font(22)
    draw.text((postit_x + 20, postit_y + 25), "📌 필수 검토 및 반려 방지 요령", font=f_p_title, fill=(133, 77, 14))

    f_p_body = get_font(20)
    draw.text((postit_x + 20, postit_y + 65), f"• {subtitle[:18]}...", font=f_p_body, fill=(30, 30, 30))
    draw.text((postit_x + 20, postit_y + 105), "• 필수 구비 서류 누락 주의", font=f_p_body, fill=(30, 30, 30))
    draw.text((postit_x + 20, postit_y + 145), "• 법정 기한 경과 전 즉시 착수", font=f_p_body, fill=(30, 30, 30))
    draw.text((postit_x + 20, postit_y + 185), "• 소관 기관 공식 심사 기준 준수", font=f_p_body, fill=(30, 30, 30))

    # Red Official Rubber Stamp (Tilted on the right side)
    stamps = ["반려주의", "필수확인", "승인완료", "실무검증"]
    stamp_txt = random.choice(stamps)
    stamp_w, stamp_h = 220, 110
    stamp_img = Image.new("RGBA", (stamp_w, stamp_h), (0, 0, 0, 0))
    s_draw = ImageDraw.Draw(stamp_img)
    # Double border stamp
    s_draw.rounded_rectangle([(5, 5), (stamp_w - 5, stamp_h - 5)], radius=12, outline=(220, 38, 38, 240), width=4)
    s_draw.rounded_rectangle([(12, 12), (stamp_w - 12, stamp_h - 12)], radius=8, outline=(220, 38, 38, 160), width=2)
    f_stamp = get_font(36)
    bbox_st = s_draw.textbbox((0, 0), stamp_txt, font=f_stamp)
    stw = bbox_st[2] - bbox_st[0]
    sth = bbox_st[3] - bbox_st[1]
    s_draw.text(((stamp_w - stw)//2, (stamp_h - sth)//2 - 4), stamp_txt, font=f_stamp, fill=(220, 38, 38, 240))
    f_sub_stamp = get_font(14)
    s_draw.text(((stamp_w - 90)//2, stamp_h - 25), "2026 VERIFIED", font=f_sub_stamp, fill=(220, 38, 38, 200))

    rotated_stamp = stamp_img.rotate(-12, resample=Image.Resampling.BICUBIC, expand=True)
    img.paste(rotated_stamp, (520, y_next + 70), rotated_stamp)

    # Bottom watermark/date
    f_bot = get_font(18)
    draw.text((90, H - 90), "대한민국 현행 법령 및 판례 기준 검토 완료", font=f_bot, fill=(150, 140, 130))

    out_buf = io.BytesIO()
    img.save(out_buf, format="JPEG", quality=95)
    return out_buf.getvalue()


# ==============================================================================
# LAYOUT 3: [Fintech Stat / Metrics] - Toss / BankSalad Dynamic Metric Card
# ==============================================================================
def render_fintech_stat(title: str, category: str = "금융/세금") -> bytes:
    # Vibrant deep emerald / indigo gradient style
    img = Image.new("RGB", (W, H), (15, 23, 42)) # Charcoal dark
    draw = ImageDraw.Draw(img)

    # Large glowing backdrop circle
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    g_draw = ImageDraw.Draw(glow)
    g_draw.ellipse([(150, 150), (650, 650)], fill=(16, 185, 129, 60)) # Emerald glow
    glow = glow.filter(ImageFilter.GaussianBlur(60))
    img.paste(Image.composite(glow.convert("RGB"), img, glow.split()[3]), (0, 0))
    draw = ImageDraw.Draw(img)

    # Top Pill Badge
    pill_text = f" 📊 {category} 핵심 지표 가이드 "
    f_pill = get_font(20)
    bbox_p = draw.textbbox((0, 0), pill_text, font=f_pill)
    pw = bbox_p[2] - bbox_p[0] + 20
    draw.rounded_rectangle([(80, 70), (80 + pw, 105)], radius=18, fill=(30, 41, 59), outline=(51, 65, 85))
    draw.text((90, 76), pill_text, font=f_pill, fill=(52, 211, 153))

    headline, subtitle = split_headline_smart(title)

    # Title
    f_title = get_font(38)
    draw.text((80, 135), headline, font=f_title, fill=(241, 245, 249))

    # Giant Stat Extraction or Dynamic Generation
    stat_val = "100%"
    stat_label = "보증금 전액 반환"
    if "억" in title or "상속" in title or "증여" in title:
        stat_val = "최대 5억원"
        stat_label = "일괄 공제 한도"
    elif "실업급여" in title:
        stat_val = "월 198만원"
        stat_label = "2026 상한 실수령액"
    elif "이자" in title or "대출" in title:
        stat_val = "연 2.5%~"
        stat_label = "정부 지원 최저 금리"
    elif "절차" in title or "신청" in title or "방법" in title:
        stat_val = "3단계"
        stat_label = "원스톱 승인 로드맵"
    elif "합의" in title or "손해배상" in title:
        stat_val = "1원 단위"
        stat_label = "실제 손해액 산출 기준"

    # Giant Stat Display
    f_stat = get_font(80)
    bbox_st = draw.textbbox((0, 0), stat_val, font=f_stat)
    stw = bbox_st[2] - bbox_st[0]
    draw.text(((W - stw)//2, 250), stat_val, font=f_stat, fill=(16, 185, 129)) # Emerald Bright

    # Stat Label Pill
    f_lbl = get_font(24)
    bbox_lbl = draw.textbbox((0, 0), stat_label, font=f_lbl)
    lw = bbox_lbl[2] - bbox_lbl[0] + 30
    draw.rounded_rectangle([((W - lw)//2, 360), ((W + lw)//2, 400)], radius=12, fill=(6, 78, 59))
    draw.text(((W - bbox_lbl[2] + bbox_lbl[0])//2, 367), stat_label, font=f_lbl, fill=(167, 243, 208))

    # Bottom 3 Metric Highlights Box
    box_y = 450
    draw.rounded_rectangle([(80, box_y), (W - 80, box_y + 240)], radius=16, fill=(30, 41, 59), outline=(51, 65, 85))

    f_row_t = get_font(22)
    f_row_v = get_font(20)

    rows = [
        ("체크포인트", subtitle[:20] if subtitle else "법정 인정 요건 충족 여부"),
        ("예방 효과", "부당 감액 및 반려 리스크 사전 차단"),
        ("기준 일자", "2026년 최신 개정 고시 및 법률 기준")
    ]

    ry = box_y + 25
    for k, v in rows:
        draw.text((110, ry), f"✔ {k}", font=f_row_t, fill=(148, 163, 184))
        draw.text((250, ry), v, font=f_row_v, fill=(248, 250, 252))
        draw.line([(110, ry + 45), (W - 110, ry + 45)], fill=(51, 65, 85), width=1)
        ry += 65

    out_buf = io.BytesIO()
    img.save(out_buf, format="JPEG", quality=95)
    return out_buf.getvalue()


# ==============================================================================
# LAYOUT 4: [Photo Duotone & Title Bar] - Curated Real Photography & News Portal
# ==============================================================================
PHOTO_CANDIDATES = [
    # Business, documents, courtroom, finance, handshake
    "https://images.unsplash.com/photo-1450133064473-71024230f91b?w=800&h=800&fit=crop&q=80",
    "https://images.unsplash.com/photo-1554224155-8d04cb21cd6c?w=800&h=800&fit=crop&q=80",
    "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=800&h=800&fit=crop&q=80",
    "https://images.unsplash.com/photo-1589829545856-d10d557cf95f?w=800&h=800&fit=crop&q=80"
]

def render_photo_duotone(title: str, category: str = "종합안내") -> bytes:
    # Try fetching real photo or fall back to gradient procedural image
    base_img = None
    try:
        photo_url = random.choice(PHOTO_CANDIDATES)
        res = requests.get(photo_url, timeout=5)
        if res.status_code == 200:
            base_img = Image.open(io.BytesIO(res.content)).convert("RGB").resize((W, H))
    except Exception:
        base_img = None

    if not base_img:
        # Procedural architectural gradient fallback
        base_img = Image.new("RGB", (W, H), (30, 41, 59))
        p_draw = ImageDraw.Draw(base_img)
        for i in range(H):
            r = int(20 + 20 * (i / H))
            g = int(30 + 30 * (i / H))
            b = int(50 + 50 * (i / H))
            p_draw.line([(0, i), (W, i)], fill=(r, g, b))

    # Apply Duotone / Dark Vignette Overlay
    overlay = Image.new("RGBA", (W, H), (15, 23, 42, 190))
    o_draw = ImageDraw.Draw(overlay)
    # Heavy dark gradient at bottom for text readability
    for i in range(H // 2, H):
        alpha = int(190 + 65 * ((i - H // 2) / (H // 2)))
        o_draw.line([(0, i), (W, i)], fill=(10, 15, 30, alpha))

    final_comp = Image.alpha_composite(base_img.convert("RGBA"), overlay).convert("RGB")
    draw = ImageDraw.Draw(final_comp)

    # Top Media Branding
    f_brand = get_font(20)
    draw.text((70, 70), "생활 속 법과 금융  |  DAILY ANALYSIS", font=f_brand, fill=(203, 213, 225))
    draw.line([(70, 105), (W - 70, 105)], fill=(100, 116, 139), width=1)

    # Category Badge
    pill_text = f" {category} "
    f_cat = get_font(22)
    bbox_c = draw.textbbox((0, 0), pill_text, font=f_cat)
    cw = bbox_c[2] - bbox_c[0] + 16
    draw.rounded_rectangle([(70, 410), (70 + cw, 450)], radius=6, fill=(234, 88, 12)) # Amber Orange
    draw.text((78, 418), pill_text, font=f_cat, fill=(255, 255, 255))

    headline, subtitle = split_headline_smart(title)

    # Title typography
    f_title = get_font(48)
    h_words = headline.split()
    if len(headline) > 13 and len(h_words) >= 2:
        h1 = " ".join(h_words[:len(h_words)//2])
        h2 = " ".join(h_words[len(h_words)//2:])
        draw.text((70, 480), h1, font=f_title, fill=(255, 255, 255))
        draw.text((70, 545), h2, font=f_title, fill=(255, 255, 255))
        sub_y = 625
    else:
        draw.text((70, 485), headline, font=f_title, fill=(255, 255, 255))
        sub_y = 560

    # Subtitle
    if subtitle:
        f_sub = get_font(26)
        draw.text((70, sub_y), subtitle[:24], font=f_sub, fill=(226, 232, 240))

    # Bottom line
    draw.line([(70, H - 70), (W - 70, H - 70)], fill=(71, 85, 105), width=2)
    f_date = get_font(18)
    draw.text((70, H - 55), "2026 최신 개정 법령 및 실무 절차 해설", font=f_date, fill=(148, 163, 184))

    out_buf = io.BytesIO()
    final_comp.save(out_buf, format="JPEG", quality=95)
    return out_buf.getvalue()


# ==============================================================================
# LAYOUT 5: [Card News 2.0] - Modernized Canva Style (with character if available)
# ==============================================================================
def render_card_news_canva(title: str, category: str = "생활법률") -> bytes:
    from image_card_news import generate_card_news_image
    return generate_card_news_image(title=title, category=category)


# ==============================================================================
# MASTER POLYMORPHIC THUMBNAIL DISPATCHER
# ==============================================================================
LAYOUT_NAMES = [
    "editorial_minimal",
    "document_stamp",
    "fintech_stat",
    "photo_duotone",
    "card_news_canva"
]

def generate_polymorphic_thumbnail(title: str, category: str = "생활법률", layout_type: str = None) -> tuple:
    """
    Intelligently generates one of 5 distinct visual thumbnail styles.
    If layout_type is not given, deterministically selects based on title hash or category.
    Returns: (image_bytes, layout_name_used)
    """
    if not layout_type:
        # Category or semantic matching
        if any(w in title for w in ["세금", "공제", "환급", "계산", "실업급여", "지원금", "이자", "금리"]):
            layout_type = "fintech_stat"
        elif any(w in title for w in ["신청", "서류", "양식", "작성법", "반려", "내용증명", "진정서"]):
            layout_type = "document_stamp"
        elif any(w in title for w in ["판례", "개정", "대법원", "칼럼", "효력", "법률안"]):
            layout_type = "editorial_minimal"
        elif any(w in title for w in ["교통사고", "사기", "보이스피싱", "피해", "분쟁"]):
            layout_type = "photo_duotone"
        else:
            # Deterministic rotation based on title
            h_idx = sum(ord(c) for c in title) % len(LAYOUT_NAMES)
            layout_type = LAYOUT_NAMES[h_idx]

    print(f"🎨 [Polymorphic Visual Engine] Selected Layout: '{layout_type}' for '{title[:25]}...'")

    if layout_type == "editorial_minimal":
        return render_editorial_minimal(title, category), "editorial_minimal"
    elif layout_type == "document_stamp":
        return render_document_stamp(title, category), "document_stamp"
    elif layout_type == "fintech_stat":
        return render_fintech_stat(title, category), "fintech_stat"
    elif layout_type == "photo_duotone":
        return render_photo_duotone(title, category), "photo_duotone"
    else:
        return render_card_news_canva(title, category), "card_news_canva"
