import requests
import json
import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

url = "https://kgamjablog.blog/wp-json/wp/v2/posts?per_page=10"
headers = {"User-Agent": "Mozilla/5.0"}
posts = requests.get(url, headers=headers).json()

print("=== Analyzing 10 Posts on kgamjablog.blog ===")
for p in posts:
    title = p.get("title", {}).get("rendered", "")
    link = p.get("link", "")
    slug = p.get("slug", "")
    excerpt = p.get("excerpt", {}).get("rendered", "").strip()
    featured_media_id = p.get("featured_media")
    content = p.get("content", {}).get("rendered", "")
    
    # Check media info
    media_url = ""
    if featured_media_id:
        try:
            m_res = requests.get(f"https://kgamjablog.blog/wp-json/wp/v2/media/{featured_media_id}", headers=headers).json()
            media_url = m_res.get("source_url", "")
        except:
            pass

    # Check images in content
    content_imgs = re.findall(r'<img [^>]*src="([^"]+)"[^>]*>', content)
    
    print(f"\n📌 제목: {title}")
    print(f"🔗 링크: {link}")
    print(f"🔤 슬러그(Slug): {slug}")
    print(f"📝 Excerpt 길이: {len(excerpt)} 글자")
    print(f"📝 Excerpt 내용: {excerpt}")
    print(f"🖼️ 대표 이미지(Featured Media): ID {featured_media_id} -> {media_url}")
    print(f"🖼️ 본문 내 이미지 개수: {len(content_imgs)}")
    if content_imgs:
        print(f"🖼️ 본문 첫 이미지: {content_imgs[0]}")
    
    # Check raw content snippet around first image or heading
    print(f"📄 본문 앞부분 샘플 (400자):\n{content[:400]}\n{'-'*60}")
