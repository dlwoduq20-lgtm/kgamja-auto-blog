'''
Home & Garden Pastel Vector Illustration Generator
Produces consistent flat vector illustrations locked to the user's pastoral style guide:
- Soft pastel palette (dusty sky blue, warm terracotta, sage green, cream)
- Rounded character shapes, modern editorial children's-book aesthetic
- Rolling hills, gentle gradient skies, soft warm sunlight glow
- Zero text, zero logos, 100% flat 2D vector illustration
'''
import urllib.parse
import random
import requests
import time

STYLE_BLOCK = (
    "Flat vector illustration style, modern editorial children's-book aesthetic. "
    "Soft pastel color palette, dusty sky blue, warm terracotta rust, olive and sage green, cream and light tan. "
    "Simple rounded character shapes with minimal facial detail, warm approachable expressions. "
    "Gentle gradient sky background with soft rounded clouds, rolling hills in background. "
    "Clean geometric shapes, no harsh outlines, soft warm sunlight glow. "
    "Strictly 2D flat vector art, no 3D rendering, no photorealism, no text, no logos, no watermarks."
)


def fetch_garden_image_bytes(generation_prompt: str) -> bytes:
    '''
    Generate and download high-resolution pastel flat vector garden illustration bytes.
    '''
    clean_prompt = generation_prompt.strip()
    if "Flat vector illustration style" not in clean_prompt:
        final_prompt = f"{clean_prompt}. {STYLE_BLOCK}"
    else:
        final_prompt = clean_prompt

    encoded = urllib.parse.quote(final_prompt)
    print(f"[Garden Illust] Generating: {clean_prompt[:70]}...")

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
                return res.content
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
