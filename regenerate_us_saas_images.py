"""
Batch Image Regenerator for US B2B SaaS Blog (StackPilot / smartlawstep)
Replaces identical static shipping banners with rich, topic-specific editorial UI banners.
"""
import sys
import os
import json
import re
import time

sys.stdout.reconfigure(encoding='utf-8')

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from image_manager_saas import generate_stackpilot_ui_banner
from blogger_client import upload_image_to_cdn

BLOG_ID_US = "1939932974175805877"

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
    print("🚀 [StackPilot US Blog] Regenerating topic-specific editorial banners...")
    posts_res = service.posts().list(blogId=BLOG_ID_US, status=['LIVE'], maxResults=50).execute()
    items = posts_res.get('items', [])
    print(f"📊 LIVE posts count: {len(items)}\n")

    results = []

    for idx, post in enumerate(items, 1):
        pid = post.get('id')
        title = post.get('title')
        labels = post.get('labels', [])
        category = labels[0] if labels else "B2B SaaS"
        content = post.get('content', '')

        print(f"--------------------------------------------------")
        print(f"[{idx}/{len(items)}] ID: {pid}")
        print(f"📌 Title: {title}")
        print(f"📂 Category: {category}")

        # 1. Generate custom banner
        banner_bytes = generate_stackpilot_ui_banner(title, category)
        if not banner_bytes:
            print("⚠️ Banner generation failed, skipping")
            continue

        # 2. Upload to CDN
        cdn_url = upload_image_to_cdn(banner_bytes)
        if not cdn_url:
            print("⚠️ CDN upload failed, skipping")
            continue
        print(f"✅ New CDN URL: {cdn_url}")

        # 3. Replace image in post content
        img_match = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', content)
        old_url = None
        if img_match:
            old_url = img_match.group(1)
            updated_content = content.replace(old_url, cdn_url, 1)
            print(f"🔄 Replaced URL: {old_url[:50]}... -> {cdn_url}")
        else:
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
            print("➕ Inserted image HTML")

        # 4. Patch post on Blogger
        try:
            service.posts().patch(
                blogId=BLOG_ID_US,
                postId=pid,
                body={"content": updated_content}
            ).execute()
            print("🎉 Blogger post patched successfully!")
            results.append({
                "id": pid,
                "title": title,
                "old_url": old_url,
                "new_url": cdn_url,
                "status": "success"
            })
        except Exception as e:
            print(f"❌ Blogger update error: {e}")
            results.append({
                "id": pid,
                "title": title,
                "status": "error",
                "error": str(e)
            })

        time.sleep(1)

    # Save backup report
    with open("remedy_us_saas_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print("\n==================================================")
    print(f"✅ All US SaaS banners replaced! Success: {len([r for r in results if r.get('status') == 'success'])}/{len(items)}")


if __name__ == '__main__':
    main()
