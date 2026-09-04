"""
Modern Digital Illustration Generator using FLUX & Gemini
Produces clean, refined, high-end editorial blog illustrations (not photorealistic).
"""
import urllib.parse
import random
import requests
import time


def fetch_flux_image_bytes(image_prompt_en: str) -> bytes:
    """
    Generate and download high-resolution modern editorial illustration bytes.
    """
    clean_prompt = image_prompt_en.strip()
    
    # Modern clean editorial digital illustration styling
    enhanced_prompt = (
        f"{clean_prompt}, modern clean editorial digital illustration, "
        f"refined clean vector aesthetic, warm soft pastel color palette, "
        f"modern Korean editorial lifestyle art, elegant minimalist design, "
        f"smooth gradient shading, crisp detailed lines, 4k resolution, "
        f"sophisticated blog illustration, no realistic photo, no watermark, no text"
    )
    
    seed = random.randint(1000, 999999)
    encoded = urllib.parse.quote(enhanced_prompt)
    flux_url = f"https://image.pollinations.ai/prompt/{encoded}?model=flux&width=1024&height=576&nologo=true&seed={seed}"
    
    print(f"🎨 [세련된 에디토리얼 일러스트 생성 중...] {image_prompt_en[:80]}...")
    
    for attempt in range(3):
        try:
            res = requests.get(flux_url, timeout=30)
            if res.status_code == 200 and len(res.content) > 5000:
                print(f"✅ 고화질 일러스트 다운로드 성공 ({len(res.content)} bytes)")
                return res.content
        except Exception as e:
            print(f"⚠️ 일러스트 다운로드 시도 {attempt+1} 실패: {e}")
            time.sleep(2)
            
    # Fallback if service times out
    try:
        fallback_res = requests.get("https://images.unsplash.com/photo-1579546929518-9e396f3cc809?w=1024&h=576&fit=crop&q=80", timeout=15)
        if fallback_res.status_code == 200:
            return fallback_res.content
    except Exception:
        pass
        
    return None
