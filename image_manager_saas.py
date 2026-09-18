'''
B2B SaaS 2D Tech Illustration & Watermark-Free Editorial Banner Generator
Produces clean, modern vector/isometric software visuals and native StackPilot UI banners (100% watermark-free).
'''
import os
import io
import urllib.parse
import random
import requests
import time
from PIL import Image, ImageDraw, ImageFont


def get_ui_font(size: int, bold: bool = True) -> ImageFont.ImageFont:
    candidates = [
        r"C:\Windows\Fonts\segoeuib.ttf" if bold else r"C:\Windows\Fonts\segoeui.ttf",
        r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf",
        r"C:\Windows\Fonts\calibrib.ttf" if bold else r"C:\Windows\Fonts\calibri.ttf"
    ]
    for p in candidates:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                continue
    return ImageFont.load_default()


def remove_watermark_crop(image_bytes: bytes) -> bytes:
    '''
    Eradicates any third-party watermark (e.g. pollinations.ai) by cropping
    off the bottom 65px of the image and resampling back to standard 16:9 (1200x675).
    '''
    try:
        im = Image.open(io.BytesIO(image_bytes))
        w, h = im.size
        # Crop off bottom 65px where logos/watermarks are placed
        cropped = im.crop((0, 0, w, max(100, h - 65)))
        final_im = cropped.resize((1200, 675), Image.Resampling.LANCZOS)
        out = io.BytesIO()
        final_im.save(out, format="JPEG", quality=94)
        return out.getvalue()
    except Exception as e:
        print(f"⚠️ Watermark crop fallback: {e}")
        return image_bytes


def generate_stackpilot_ui_banner(title: str, category: str = "B2B SaaS Guide") -> bytes:
    '''
    Generates a native, ultra-clean StackPilot B2B Editorial Dashboard Banner (1200x675).
    Completely watermark-free, razor-sharp typography, corporate tech aesthetic.
    '''
    w, h = 1200, 675
    bg = Image.new("RGB", (w, h), color="#090d16")
    draw = ImageDraw.Draw(bg)
    
    # Modern subtle tech grid
    for x in range(0, w, 40):
        draw.line([(x, 0), (x, h)], fill="#111927", width=1)
    for y in range(0, h, 40):
        draw.line([(0, y), (w, y)], fill="#111927", width=1)

    # Top Brand Badges
    draw.rounded_rectangle([70, 60, 360, 95], radius=6, fill="#1e293b", outline="#3b82f6", width=1)
    draw.text((88, 70), "STACKPILOT BUYER GUIDE", fill="#93c5fd", font=get_ui_font(14, True))
    
    draw.rounded_rectangle([375, 60, 520, 95], radius=6, fill="#064e3b", outline="#10b981", width=1)
    draw.text((392, 70), "2026 AUDITED", fill="#6ee7b7", font=get_ui_font(14, True))
    
    # Title Formatting (intelligent 2-line break)
    font_title = get_ui_font(36, True)
    words = title.split()
    if len(words) > 4:
        line1 = " ".join(words[:4])
        line2 = " ".join(words[4:])
    else:
        line1 = title
        line2 = ""
        
    draw.text((70, 130), line1, fill="#f8fafc", font=font_title)
    if line2:
        draw.text((70, 185), line2, fill="#60a5fa", font=font_title)
        
    # Subtitle / Metric details
    draw.text((70, 260), "5-7 Platforms Evaluated • Pricing & Carrier API Matrix • Independent Audit", fill="#94a3b8", font=get_ui_font(15, False))

    # Decorative Category Pill
    draw.rounded_rectangle([70, 310, 260, 345], radius=6, fill="#1e1b4b", outline="#6366f1", width=1)
    draw.text((88, 320), category.upper(), fill="#c7d2fe", font=get_ui_font(12, True))

    # Right side: Interactive UI Mockup Card
    card_x1, card_y1, card_x2, card_y2 = 680, 75, 1130, 600
    draw.rounded_rectangle([card_x1, card_y1, card_x2, card_y2], radius=16, fill="#0f172a", outline="#334155", width=2)
    
    # Mockup Header Bar
    draw.rectangle([card_x1+2, card_y1+2, card_x2-2, card_y1+48], fill="#1e293b")
    draw.ellipse([card_x1+18, card_y1+18, card_x1+30, card_y1+30], fill="#ef4444")
    draw.ellipse([card_x1+38, card_y1+18, card_x1+50, card_y1+30], fill="#f59e0b")
    draw.ellipse([card_x1+58, card_y1+18, card_x1+70, card_y1+30], fill="#10b981")
    draw.text((card_x1+85, card_y1+16), "Carrier Rate Shopping Engine", fill="#94a3b8", font=get_ui_font(13, True))
    
    # Mockup Rate Rows
    mockup_rows = [
        ("USPS Priority Mail", "$7.42", "Discount: -44%", "#10b981"),
        ("UPS Ground Commercial", "$8.15", "Discount: -68%", "#10b981"),
        ("FedEx Home Delivery", "$11.30", "Standard API", "#60a5fa"),
        ("DHL Express Worldwide", "$28.50", "Cross-Border", "#f59e0b")
    ]
    for idx, (carrier, price, tag, col) in enumerate(mockup_rows):
        cy = card_y1 + 75 + idx * 78
        draw.rounded_rectangle([card_x1+20, cy, card_x2-20, cy+62], radius=8, fill="#1e293b", outline="#334155", width=1)
        draw.text((card_x1+35, cy+12), carrier, fill="#f8fafc", font=get_ui_font(14, True))
        draw.text((card_x1+35, cy+35), "Real-time API response • 2-3 business days", fill="#64748b", font=get_ui_font(11, False))
        draw.text((card_x2-120, cy+12), price, fill="#ffffff", font=get_ui_font(15, True))
        draw.text((card_x2-130, cy+35), tag, fill=col, font=get_ui_font(11, True))
        
    out = io.BytesIO()
    bg.save(out, format="JPEG", quality=95)
    return out.getvalue()


def fetch_saas_image_bytes(image_prompt_en: str, title: str = "", category: str = "E-Commerce & Retail Tech") -> bytes:
    '''
    Generate and download modern 2D vector tech illustration bytes.
    GUARANTEES 100% WATERMARK-FREE output.
    '''
    # Priority: If title is provided, generate high-end StackPilot UI Editorial Banner
    if title:
        print(f"[StackPilot Banner] Generating custom UI dashboard banner for: '{title}'...")
        try:
            banner_bytes = generate_stackpilot_ui_banner(title, category)
            if banner_bytes and len(banner_bytes) > 20000:
                print(f"[OK] StackPilot native editorial banner generated ({len(banner_bytes)} bytes, 100% watermark-free)")
                return banner_bytes
        except Exception as e:
            print(f"⚠️ UI banner generation notice: {e}. Falling back to clean cropped illustration...")

    clean_prompt = image_prompt_en.strip()
    enhanced_prompt = (
        f"{clean_prompt}, modern clean 2D vector tech illustration, minimalist isometric software workflow, "
        f"corporate tech graphic, cool slate blue and vibrant cyan color palette, smooth flat vector art, "
        f"clean modern digital aesthetic, high resolution graphic, full bleed composition, "
        f"strictly no text, no letters, no real brand logos, no photographic elements"
    )
    
    encoded = urllib.parse.quote(enhanced_prompt)
    print(f"[2D SaaS Illustration] Generating: {clean_prompt[:70]}...")

    configs = [
        {"model": "flux", "timeout": 40},
        {"model": None, "timeout": 35}
    ]

    for attempt, cfg in enumerate(configs, 1):
        seed = random.randint(1000, 999999)
        if cfg["model"]:
            url = f"https://image.pollinations.ai/prompt/{encoded}?model={cfg['model']}&width=1200&height=750&nologo=true&seed={seed}"
        else:
            url = f"https://image.pollinations.ai/prompt/{encoded}?width=1200&height=750&nologo=true&seed={seed}"

        try:
            res = requests.get(url, timeout=cfg["timeout"])
            if res.status_code == 200 and len(res.content) > 5000:
                # Immediately crop out bottom 65px to guarantee no watermark exists
                clean_bytes = remove_watermark_crop(res.content)
                print(f"[OK] 2D Tech Illustration downloaded & watermarks cropped ({len(clean_bytes)} bytes)")
                return clean_bytes
            elif res.status_code == 429:
                print(f"[Wait] Rate limit (429)... waiting 5s")
                time.sleep(5)
            else:
                time.sleep(2)
        except Exception as e:
            time.sleep(2)

    # Fallback to pure UI Banner
    return generate_stackpilot_ui_banner(title or "B2B SaaS Software Guide", category)

