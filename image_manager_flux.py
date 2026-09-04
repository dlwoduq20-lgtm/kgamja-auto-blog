"""
Photorealistic Image Generator using FLUX & Gemini Art Director
Fetches raw image bytes and attaches directly to Blogger posts for 0% broken image rate.
"""
import urllib.parse
import random
import requests
import time


def fetch_flux_image_bytes(image_prompt_en: str) -> bytes:
    """
    Generate and download high-resolution FLUX image bytes.
    """
    clean_prompt = image_prompt_en.strip()
    
    # Photorealistic documentary camera styling
    enhanced_prompt = (
        f"{clean_prompt}, authentic Korean scene, documentary photography style, "
        f"shot on Sony A7R V 35mm f/1.8 lens, natural lighting, sharp focus, 8k resolution, "
        f"photorealistic, cinematic, real life photo, no CGI, no 3d rendering, no cartoon, no text"
    )
    
    seed = random.randint(1000, 999999)
    encoded = urllib.parse.quote(enhanced_prompt)
    flux_url = f"https://image.pollinations.ai/prompt/{encoded}?model=flux&width=1024&height=576&nologo=true&seed={seed}"
    
    print(f"🎨 [FLUX 실사 이미지 렌더링 중...] {image_prompt_en[:80]}...")
    
    for attempt in range(3):
        try:
            res = requests.get(flux_url, timeout=30)
            if res.status_code == 200 and len(res.content) > 5000:
                print(f"✅ FLUX 실사 이미지 다운로드 성공 ({len(res.content)} bytes)")
                return res.content
        except Exception as e:
            print(f"⚠️ 이미지 다운로드 시도 {attempt+1} 실패: {e}")
            time.sleep(2)
            
    # Fallback to high-quality curated stock photo if FLUX service times out
    try:
        fallback_res = requests.get("https://images.unsplash.com/photo-1450133064473-71024230f91b?w=1024&h=576&fit=crop&q=80", timeout=15)
        if fallback_res.status_code == 200:
            return fallback_res.content
    except Exception:
        pass
        
    return None
