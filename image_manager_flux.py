"""
2D Retro Instatoon & Vintage Pop Art Comic Art Generator using Pollinations AI
Produces distinctive 2D retro illustrations matching the user's concept:
- Bold black ink hatching / engraving linework
- Cool relatable character with retro sunglasses
- Vintage pop art color palette (forest green, warm antique paper, mustard yellow)
- Strictly 2D flat illustration (no 3D rendering, no photorealism, no airbrush blur)
"""
import urllib.parse
import random
import requests
import time


def fetch_flux_image_bytes(image_prompt_en: str) -> bytes:
    """
    Generate and download high-resolution 2D retro instatoon / vintage pop art illustration bytes.
    Uses FLUX and high-speed fallback models with robust retry and rate-limit handling.
    """
    clean_prompt = image_prompt_en.strip()
    
    # Core aesthetic prompt formula matching user reference
    enhanced_prompt = (
        f"{clean_prompt}, vintage retro pop art comic engraving illustration with vibrant retro colors, "
        f"cool character wearing retro sunglasses and baseball cap, witty relatable smirk, "
        f"fine black ink cross-hatching linework, retro screen-print graphic art, "
        f"muted forest green and warm mustard yellow tones, antique paper texture, "
        f"strictly 2D flat drawing, no 3D rendering, no soft blur, no airbrush shading, no realism, no text"
    )
    
    encoded = urllib.parse.quote(enhanced_prompt)
    print(f"[2D Retro Instatoon] Generating: {clean_prompt[:70]}...")

    # Generation attempts: Try FLUX first, then high-speed default model with seed variations
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
                print(f"[OK] 2D 레트로 일러스트 생성 성공 ({len(res.content)} bytes, attempt {attempt})")
                return res.content
            elif res.status_code == 429:
                print(f"[Wait] Pollinations rate limit (429)... waiting 10s")
                time.sleep(10)
            else:
                print(f"[Warning] 일러스트 생성 시도 {attempt} HTTP {res.status_code}")
                time.sleep(3)
        except Exception as e:
            print(f"[Warning] 일러스트 생성 시도 {attempt} error: {e}")
            time.sleep(3)

    # Reliable fallback image if external generator is completely down
    print("[Fallback] 기본 레트로 그래픽 대체 로딩...")
    try:
        fallback_res = requests.get(
            "https://images.unsplash.com/photo-1579546929518-9e396f3cc809?w=1024&h=576&fit=crop&q=80",
            timeout=15
        )
        if fallback_res.status_code == 200:
            return fallback_res.content
    except Exception:
        pass

    return None
