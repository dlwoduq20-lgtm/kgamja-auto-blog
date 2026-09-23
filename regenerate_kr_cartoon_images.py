"""
Batch Cartoon Image Regenerator for Korean Blog (kgamjablog)
Converts all LIVE posts on kgamjablog to high-quality 2D cartoon / webtoon thumbnails,
uploads to Catbox CDN, and updates Blogger posts via REST API.
"""
import sys
import os
import json
import re
import time

sys.stdout.reconfigure(encoding='utf-8')

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from image_manager_chatgpt import fetch_cartoon_thumbnail_bytes
from blogger_client import upload_image_to_cdn, BLOG_ID_KR

# Load credentials
with open('blogger_credentials.json', 'r', encoding='utf-8') as f:
    creds_dict = json.load(f)

creds = Credentials(
    token=creds_dict.get('token'),
    refresh_token=creds_dict.get('refresh_token'),
    token_uri='https://oauth2.googleapis.com/token',
    client_id=creds_dict.get('client_id'),
    client_secret=creds_dict.get('client_secret'),
    scopes=['https://www.googleapis.com/auth/blogger']
)
service = build('blogger', 'v3', credentials=creds)


def main():
    print("🚀 [Kgamja Blog] 2D 카툰 썸네일 전면 교체 작업 시작...")
    posts_res = service.posts().list(blogId=BLOG_ID_KR, status=['LIVE'], maxResults=50).execute()
    items = posts_res.get('items', [])
    print(f"📊 대상 LIVE 포스트 수: {len(items)}개\n")

    results = []

    for idx, post in enumerate(items, 1):
        pid = post.get('id')
        title = post.get('title')
        labels = post.get('labels', [])
        category = labels[0] if labels else "생활법률"
        content = post.get('content', '')

        print(f"--------------------------------------------------")
        print(f"[{idx}/{len(items)}] ID: {pid}")
        print(f"📌 제목: {title}")
        print(f"📂 카테고리: {category}")

        # 1. Generate 2D cartoon thumbnail
        print("🎨 2D 카툰 썸네일 생성 중...")
        image_bytes = fetch_cartoon_thumbnail_bytes(title, category=category)
        if not image_bytes:
            print("⚠️ 썸네일 생성 실패, 건너뜀")
            continue

        # 2. Upload to CDN (Catbox)
        print("☁️ Catbox CDN 업로드 중...")
        cdn_url = upload_image_to_cdn(image_bytes)
        if not cdn_url:
            print("⚠️ CDN 업로드 실패, 건너뜀")
            continue
        print(f"✅ 새 CDN 썸네일 URL: {cdn_url}")

        # 3. Replace image in post content
        img_match = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', content)
        old_url = None
        if img_match:
            old_url = img_match.group(1)
            updated_content = content.replace(old_url, cdn_url, 1)
            print(f"🔄 기존 이미지 URL 교체: {old_url[:50]}... -> {cdn_url}")
        else:
            # If no image tag, insert right after <!--more--> or lead paragraph
            image_html = (
                f'<div style="text-align: center; margin: 0 0 25px 0;">\n'
                f'  <img src="{cdn_url}" alt="{title}" '
                f'style="max-width: 100%; height: auto; border-radius: 12px; box-shadow: 0 4px 16px rgba(0,0,0,0.12); display: inline-block;" />\n'
                f'</div>\n\n'
            )
            if "<!--more-->" in content:
                updated_content = content.replace("<!--more-->", f"<!--more-->\n{image_html}", 1)
            else:
                updated_content = image_html + content
            print("➕ 신규 이미지 태그 삽입 완료")

        # 4. Patch post on Blogger
        try:
            service.posts().patch(
                blogId=BLOG_ID_KR,
                postId=pid,
                body={"content": updated_content}
            ).execute()
            print("🎉 블로거 업데이트 성공!")
            results.append({
                "id": pid,
                "title": title,
                "old_url": old_url,
                "new_url": cdn_url,
                "status": "success"
            })
        except Exception as e:
            print(f"❌ 블로거 업데이트 에러: {e}")
            results.append({
                "id": pid,
                "title": title,
                "status": "error",
                "error": str(e)
            })

        # Polite interval to avoid hammering APIs
        time.sleep(2)

    # Save backup report
    with open("remedy_kr_cartoon_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print("\n==================================================")
    print(f"✅ 전체 2D 카툰 교체 완료! 성공: {len([r for r in results if r.get('status') == 'success'])}/{len(items)}")


if __name__ == '__main__':
    main()
