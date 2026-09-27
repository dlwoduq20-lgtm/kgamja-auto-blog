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
from image_card_news import generate_card_news_image
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

        # 1. Generate 2D Canva card-news thumbnail
        print("🎨 2D 캔바/카드뉴스 스타일 썸네일 생성 중...")
        image_bytes = generate_card_news_image(title=title, category=category, palette_index=idx)
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
        # 3. Replace image in post content and ensure it is placed BEFORE <!--more-->
        new_img_tag = (
            f'<div class="separator" style="clear: both; text-align: center; margin: 0 0 25px 0;">\n'
            f'  <a href="{cdn_url}" style="margin-left: 1em; margin-right: 1em;">\n'
            f'    <img border="0" data-original-height="800" data-original-width="800" src="{cdn_url}" alt="{title}" '
            f'style="max-width: 100%; height: auto; border-radius: 12px; box-shadow: 0 4px 16px rgba(0,0,0,0.12); display: inline-block;" />\n'
            f'  </a>\n'
            f'</div>\n\n'
        )

        img_match = re.search(r'(<div[^>]*class=["\']separator["\'][^>]*>.*?</div>|<div[^>]*text-align:\s*center[^>]*>.*?<img[^>]+>.*?</div>|<img[^>]+>)', content, re.S)
        if img_match:
            old_img_block = img_match.group(1)
            # Remove old image block
            content_no_img = content.replace(old_img_block, '', 1).strip()
            # Insert new image block at the very top before <!--more-->
            if "<!--more-->" in content_no_img:
                updated_content = f"{new_img_tag}{content_no_img}"
            else:
                updated_content = f"{new_img_tag}<!--more-->\n{content_no_img}"
            print(f"🔄 기존 이미지 제거 후 최상단(<!--more--> 이전)에 새 카드뉴스 썸네일 재배치 완료")
        else:
            # If no image tag, insert right after <!--more--> or lead paragraph
            image_html = (
                f'<div class="separator" style="clear: both; text-align: center; margin: 0 0 25px 0;">\n'
                f'  <a href="{cdn_url}" style="margin-left: 1em; margin-right: 1em;">\n'
                f'    <img border="0" data-original-height="800" data-original-width="800" src="{cdn_url}" alt="{title}" '
                f'style="max-width: 100%; height: auto; border-radius: 12px; box-shadow: 0 4px 16px rgba(0,0,0,0.12); display: inline-block;" />\n'
                f'  </a>\n'
                f'</div>\n\n'
            )
            if "<!--more-->" in content:
                updated_content = content.replace("<!--more-->", f"{image_html}<!--more-->", 1)
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
