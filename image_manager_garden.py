'''
Home & Garden Pastel Vector Illustration Generator
Produces consistent flat vector illustrations locked to the user's pastoral style guide:
- Soft pastel palette (dusty sky blue, warm terracotta, sage green, cream)
- Rounded character shapes, modern editorial children's-book aesthetic
- Rolling hills, gentle gradient skies, soft warm sunlight glow
- Zero text, zero logos, 100% flat 2D vector illustration
'''
import io
import urllib.parse
import random
import requests
import time
from PIL import Image

STYLE_BLOCK = (
    "flat vector illustration style, modern editorial gardening children's-book aesthetic, "
    "soft pastel color palette with warm terracotta, olive and sage green, cream, and dusty sky blue, "
    "simple rounded character shapes with warm approachable expressions, "
    "clean geometric vector shapes, gentle warm sunlight glow, "
    "strictly 2D flat vector art, no 3D rendering, no photorealism, no text, no logos, no watermarks, no barren empty landscape"
)


def remove_watermark_crop(image_bytes: bytes) -> bytes:
    '''
    Eradicates any third-party watermark (e.g. pollinations.ai) by cropping
    off the bottom 65px of the image and resampling back to standard 16:9 (1024x576).
    '''
    try:
        im = Image.open(io.BytesIO(image_bytes))
        w, h = im.size
        cropped = im.crop((0, 0, w, max(100, h - 65)))
        final_im = cropped.resize((1024, 576), Image.Resampling.LANCZOS)
        out = io.BytesIO()
        final_im.save(out, format="JPEG", quality=94)
        return out.getvalue()
    except Exception as e:
        print(f"⚠️ Garden watermark crop fallback: {e}")
        return image_bytes


def fetch_garden_image_bytes(generation_prompt: str) -> bytes:
    '''
    Generate and download high-resolution pastel flat vector garden illustration bytes.
    Ensures the specific crops and gardening subject are in the foreground.
    '''
    clean_prompt = generation_prompt.strip()
    
    # Strip any leading style block prefix to guarantee subject comes FIRST
    lower_prompt = clean_prompt.lower()
    if lower_prompt.startswith("flat vector illustration style"):
        # Find where the scene detail was appended
        markers = ["no brand references.", "no text.", "aesthetic."]
        extracted_subject = ""
        for marker in markers:
            if marker in lower_prompt:
                idx = lower_prompt.find(marker) + len(marker)
                extracted_subject = clean_prompt[idx:].strip(" .-,")
                break
        if extracted_subject:
            final_prompt = f"{extracted_subject}, clear foreground focus on organic vegetables and plants, {STYLE_BLOCK}"
        else:
            final_prompt = f"{clean_prompt}, {STYLE_BLOCK}"
    elif "flat vector illustration style" not in lower_prompt:
        final_prompt = f"{clean_prompt}, clear foreground focus on organic vegetables and plants, {STYLE_BLOCK}"
    else:
        final_prompt = clean_prompt

    encoded = urllib.parse.quote(final_prompt)
    print(f"[Garden Illust] Generating: {final_prompt[:80]}...")

    configs = [
        {"model": None, "timeout": 35},
        {"model": "flux", "timeout": 45},
        {"model": None, "timeout": 35}
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
                print(f"[OK] Garden illustration downloaded ({len(res.content)} bytes, attempt {attempt})")
                return remove_watermark_crop(res.content)
            elif res.status_code == 429:
                print(f"[Wait] Pollinations rate limit (429)... waiting 10s")
                time.sleep(10)
            else:
                print(f"[Warning] Garden illustration attempt {attempt} HTTP {res.status_code}")
                time.sleep(3)
        except Exception as e:
            print(f"[Warning] Garden illustration attempt {attempt} error: {e}")
            time.sleep(3)

    # Fallback to high-quality pastoral garden image
    print("[Fallback] Loading fallback pastoral garden illustration...")
    try:
        fallback_res = requests.get(
            "https://images.unsplash.com/photo-1585320806297-9794b3e4eeae?w=1024&h=576&fit=crop&q=80",
            timeout=15
        )
        if fallback_res.status_code == 200:
            return fallback_res.content
    except Exception:
        pass

    return None
