"""
Korean 2D Webtoon / Comic Art Generator using FLUX & Gemini
Produces clean, expressive 2D manhwa / comic book style illustrations (만화, 웹툰 그림 형태).
"""
import urllib.parse
import random
import requests
import time


def fetch_flux_image_bytes(image_prompt_en: str) -> bytes:
    """
    Generate and download high-resolution Korean 2D webtoon / comic art bytes.
    """
    clean_prompt = image_prompt_en.strip()
    
    # Pure 2D Korean Webtoon / Manhwa comic art styling
    enhanced_prompt = (
        f"{clean_prompt}, Korean webtoon style 2D comic art, colored digital manhwa drawing, "
        f"clean black line art, cel shaded 2D cartoon style, expressive relatable emotions, "
        f"vibrant flat colors, high quality 2D webtoon illustration, full bleed scene, "
        f"strictly no real photo, no 3D rendering, no physical book, no text"
    )
    
    seed = random.randint(1000, 999999)
    encoded = urllib.parse.quote(enhanced_prompt)
    flux_url = f"https://image.pollinations.ai/prompt/{encoded}?model=flux&width=1024&height=576&nologo=true&seed={seed}"
    
    print(f"🎨 [2D 웹툰/만화 스타일 이미지 생성 중...] {image_prompt_en[:80]}...")
    
    for attempt in range(3):
        try:
            res = requests.get(flux_url, timeout=30)
            if res.status_code == 200 and len(res.content) > 5000:
                print(f"✅ 2D 웹툰 일러스트 다운로드 성공 ({len(res.content)} bytes)")
                return res.content
        except Exception as e:
            print(f"⚠️ 웹툰 이미지 다운로드 시도 {attempt+1} 실패: {e}")
            time.sleep(2)
            
    # Fallback if service times out
    try:
        fallback_res = requests.get("https://images.unsplash.com/photo-1579546929518-9e396f3cc809?w=1024&h=576&fit=crop&q=80", timeout=15)
        if fallback_res.status_code == 200:
            return fallback_res.content
    except Exception:
        pass
        
    return None
