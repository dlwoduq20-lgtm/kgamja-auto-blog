'''
B2B SaaS 2D Tech Illustration & Modern Vector Graphic Generator using FLUX
Produces clean, modern vector/isometric software visuals (no real brand logos, professional aesthetic).
'''
import urllib.parse
import random
import requests
import time


def fetch_saas_image_bytes(image_prompt_en: str) -> bytes:
    '''
    Generate and download modern 2D vector tech illustration bytes.
    '''
    clean_prompt = image_prompt_en.strip()
    
    enhanced_prompt = (
        f"{clean_prompt}, modern clean 2D vector tech illustration, minimalist isometric software workflow, "
        f"corporate tech graphic, cool slate blue and vibrant cyan color palette, smooth flat vector art, "
        f"clean modern digital aesthetic, high resolution graphic, full bleed composition, "
        f"strictly no text, no letters, no real brand logos, no photographic elements"
    )
    
    seed = random.randint(1000, 999999)
    encoded = urllib.parse.quote(enhanced_prompt)
    print(f"[2D SaaS Illustration] Generating: {clean_prompt[:70]}...")

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
                print(f"[OK] 2D Tech Illustration downloaded ({len(res.content)} bytes, attempt {attempt})")
                return res.content
            elif res.status_code == 429:
                print(f"[Wait] Pollinations rate limit (429)... waiting 10s")
                time.sleep(10)
            else:
                print(f"[Warning] Tech Illustration attempt {attempt} HTTP {res.status_code}")
                time.sleep(3)
        except Exception as e:
            print(f"[Warning] Tech Illustration attempt {attempt} error: {e}")
            time.sleep(3)

    # Fallback
    print("[Fallback] Loading fallback tech illustration...")
    try:
        fallback_res = requests.get(
            "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=1024&h=576&fit=crop&q=80",
            timeout=15
        )
        if fallback_res.status_code == 200:
            return fallback_res.content
    except Exception:
        pass

    return None
