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
    flux_url = f"https://image.pollinations.ai/prompt/{encoded}?model=flux&width=1024&height=576&nologo=true&seed={seed}"
    
    print(f"🎨 [Generating 2D SaaS Tech Illustration...] {image_prompt_en[:80]}...")
    
    for attempt in range(3):
        try:
            res = requests.get(flux_url, timeout=30)
            if res.status_code == 200 and len(res.content) > 5000:
                print(f"✅ 2D Tech Illustration downloaded successfully ({len(res.content)} bytes)")
                return res.content
        except Exception as e:
            print(f"⚠️ Image download attempt {attempt+1} failed: {e}")
            time.sleep(2)
            
    # Fallback
    try:
        fallback_res = requests.get("https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=1024&h=576&fit=crop&q=80", timeout=15)
        if fallback_res.status_code == 200:
            return fallback_res.content
    except Exception:
        pass
        
    return None
