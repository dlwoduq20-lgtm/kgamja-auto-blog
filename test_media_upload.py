import requests
import sys
sys.path.insert(0, r'C:\Users\dlwod\.gemini\antigravity\scratch\kgamja_auto_blog')
from config import WP_URL, WP_USER, WP_APP_PASSWORD

sys.stdout.reconfigure(encoding='utf-8')

# Download a sample legal/finance image
test_img_url = "https://images.unsplash.com/photo-1450133064473-71024230f91b?w=800&q=80"
r_img = requests.get(test_img_url, timeout=15)
img_bytes = r_img.content

# Upload to WordPress media library
headers = {
    'Content-Disposition': 'attachment; filename="legal_guide_thumbnail.jpg"',
    'Content-Type': 'image/jpeg'
}

r = requests.post(f"{WP_URL}/wp-json/wp/v2/media", auth=(WP_USER, WP_APP_PASSWORD), headers=headers, data=img_bytes, timeout=30)
print("Media Upload Status:", r.status_code)
if r.status_code in (200, 201):
    data = r.json()
    media_id = data.get("id")
    source_url = data.get("source_url")
    print(f"Media ID: {media_id}")
    print(f"Source URL: {source_url}")
else:
    print(r.text[:300])
