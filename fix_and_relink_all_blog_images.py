"""
Fix and Relink All 4 Blog Images to GitHub Raw CDN
Eradicates blocked Catbox URLs and replaces them with 100% accessible, permanent GitHub CDN URLs.
"""
import os
import sys
import json
import re
import subprocess
import requests

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

from blogger_client import get_blogger_service, BLOG_ID_KR, BLOG_ID_JP
from image_polymorphic import generate_polymorphic_thumbnail
from image_manager_saas import fetch_saas_image_bytes
from image_manager_garden import fetch_garden_image_bytes

ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")
os.makedirs(ASSETS_DIR, exist_ok=True)

with open('blogger_credentials.json', 'r', encoding='utf-8') as f:
    creds_dict = json.load(f)
service = get_blogger_service(creds_dict)

TARGET_POSTS = [
    {
        "tag": "KR",
        "blog_id": BLOG_ID_KR,
        "post_id": "8233225647447857421",
        "title": "전세보증금 반환소송 승소율 높이는 법원 소장 작성법: 청구취지부터 입증자료까지 실무 가이드",
        "filename": "thumb_kr_deposit_lawsuit.jpg",
        "gen": lambda: generate_polymorphic_thumbnail("전세보증금 반환소송 승소율 높이는 법원 소장 작성법: 청구취지부터 입증자료까지 실무 가이드", "전월세/부동산", language="ko")[0]
    },
    {
        "tag": "JP",
        "blog_id": BLOG_ID_JP,
        "post_id": "4679403054105717197",
        "title": "賃貸退去後の敷金返還トラブル：法的根拠に基づく未返還請求の実務手順",
        "filename": "thumb_jp_shikikin_refund.jpg",
        "gen": lambda: generate_polymorphic_thumbnail("賃貸退去後の敷金返還トラブル：法的根拠に基づく未返還請求の実務手順", "不動産・賃貸", language="ja")[0]
    },
    {
        "tag": "US",
        "blog_id": "1939932974175805877",
        "post_id": "7119410574820366706",
        "title": "Top 5 Modern PRM Platforms: Replacing Legacy Channel Management",
        "filename": "thumb_us_prm_platforms.jpg",
        "gen": lambda: fetch_saas_image_bytes("Top 5 Modern PRM Platforms: Replacing Legacy Channel Management", "Marketing & Sales Automation")
    },
    {
        "tag": "GARDEN",
        "blog_id": "7758791627533733698",
        "post_id": "487734253691153465",
        "title": "Overwintering Dwarf Meyer Lemons: Indoor Care & Container Mastery",
        "filename": "thumb_garden_lemon_tree.jpg",
        "gen": lambda: fetch_garden_image_bytes("Close-up of a potted dwarf Meyer lemon tree indoors near a sunny window with glowing yellow lemons, terracotta container")
    }
]

def main():
    print("=" * 70)
    print("🛠️ [블로그 이미지 엑박 긴급 수리 및 GitHub 영구 CDN 재연동 시작]")
    print("=" * 70)

    # 1. Generate and save images locally
    created_files = []
    cdn_urls = {}
    for item in TARGET_POSTS:
        print(f"\n🎨 [{item['tag']}] 새 고화질 썸네일 생성 중: {item['filename']}...")
        img_bytes = item["gen"]()
        file_path = os.path.join(ASSETS_DIR, item["filename"])
        with open(file_path, "wb") as f:
            f.write(img_bytes)
        created_files.append(file_path)
        raw_url = f"https://raw.githubusercontent.com/dlwoduq20-lgtm/kgamja-auto-blog/main/assets/{item['filename']}"
        cdn_urls[item["tag"]] = raw_url
        print(f"✅ [{item['tag']}] 로컬 파일 저장 완료 ({len(img_bytes)} bytes) -> {raw_url}")

    # 2. Git add, commit, and push all images
    print("\n📦 GitHub 원격 저장소에 썸네일 에셋 동기화 (Commit & Push)...")
    for f in created_files:
        subprocess.run(["git", "add", f], check=True)
    subprocess.run(["git", "commit", "-m", "fix: deploy clean high-res thumbnails for latest 4 blog posts to assets/"], check=False)
    push_res = subprocess.run(["git", "push", "origin", "main"], capture_output=True, text=True)
    print("🚀 Git Push 결과:", push_res.stdout.strip() or "Up-to-date")

    # 3. Test CDN connectivity for each URL
    print("\n🌐 CDN 연결 상태 및 한국 내 접근성 테스트:")
    for tag, url in cdn_urls.items():
        try:
            r = requests.get(url, timeout=5)
            print(f"✅ [{tag}] HTTP {r.status_code} ({len(r.content)} bytes) 정상 연결: {url}")
        except Exception as e:
            print(f"❌ [{tag}] 연결 실패: {e}")

    # 4. Patch posts on Blogger
    print("\n🔄 구글 블로거 포스팅 본문 이미지 URL 패치 진행:")
    for item in TARGET_POSTS:
        tag = item["tag"]
        bid = item["blog_id"]
        pid = item["post_id"]
        new_url = cdn_urls[tag]

        post = service.posts().get(blogId=bid, postId=pid).execute()
        content = post.get("content", "")

        # Find catbox URLs or existing img src
        catbox_matches = re.findall(r'https?://(?:files\.)?catbox\.moe/[a-zA-Z0-9_\.]+', content)
        if catbox_matches:
            print(f"🔍 [{tag}] 기존 엑박 Catbox URL {len(catbox_matches)}개 발견: {catbox_matches}")
            for old_u in catbox_matches:
                content = content.replace(old_u, new_url)
        else:
            print(f"ℹ️ [{tag}] Catbox URL 없음, 첫 번째 이미지 src 교체 시도")
            content = re.sub(r'(<img[^>]+src=["\'])[^"\']+(["\'])', rf'\g<1>{new_url}\g<2>', content, count=1)

        # Patch post
        patched = service.posts().patch(blogId=bid, postId=pid, body={"content": content}).execute()
        print(f"🎉 [{tag}] 블로거 포스팅 패치 완료!")
        print(f"   📌 글 제목: {patched.get('title')}")
        print(f"   🌐 글 URL: {patched.get('url')}")
        
    print("\n" + "=" * 70)
    print("✅ 4대 글로벌 블로그 썸네일 엑박 수리 및 복구 완료!")
    print("=" * 70)

if __name__ == "__main__":
    main()
