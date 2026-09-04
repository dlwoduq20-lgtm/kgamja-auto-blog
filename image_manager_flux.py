"""
Photorealistic Image Generator using FLUX & Gemini Art Director
Produces realistic, professional documentary-style photography for blog posts.
"""
import urllib.parse
import random


def generate_flux_image_url(image_prompt_en: str) -> str:
    """
    Generate a direct high-resolution FLUX image URL.
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
    return flux_url


def insert_flux_image_into_content(content_html: str, image_url: str, alt_text: str) -> str:
    """
    Embed the FLUX photorealistic image cleanly right after the opening paragraph or 1st H2.
    """
    if not image_url:
        return content_html

    image_block = f"""
<div style="text-align: center; margin: 30px auto; max-width: 720px;">
  <img src="{image_url}" alt="{alt_text}" style="width: 100%; height: auto; border-radius: 10px; box-shadow: 0 4px 16px rgba(0,0,0,0.12);" />
  <p style="color: #777; font-size: 13px; margin-top: 8px; text-align: center;">▲ {alt_text}</p>
</div>
"""
    first_p = content_html.find("</p>")
    if first_p != -1:
        insert_idx = first_p + 4
        return content_html[:insert_idx] + "\n" + image_block + "\n" + content_html[insert_idx:]
    
    first_h2 = content_html.find("</h2>")
    if first_h2 != -1:
        insert_idx = first_h2 + 5
        return content_html[:insert_idx] + "\n" + image_block + "\n" + content_html[insert_idx:]

    return image_block + "\n" + content_html
