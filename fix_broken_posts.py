"""
Fix broken and missing images across Blogger posts.
Replaces dead external URLs with 100% self-hosted Base64 2D retro instatoon illustrations.
Cleans up duplicate/empty test posts.
"""
import sys
import os
import json
import re
import base64
import time

sys.stdout.reconfigure(encoding='utf-8')

from blogger_client import get_blogger_service, BLOG_ID_KR, BLOG_ID_JP
from image_manager_flux import fetch_flux_image_bytes

KR_POSTS_TO_FIX = [
    {
        "id": "6658118133507262002",
        "title": "변호사 비용 0원으로 300만 원 빌려준 돈 받아낸 실제 과정",
        "prompt": "A triumphant everyday Korean person holding small claims court repayment document with confident smirk at cafe, retro sunglasses and cap, vintage pop art"
    },
    {
        "id": "3803943468899584396",
        "title": "신용회복위원회 워크아웃 중 급여 압류 100% 방지, 압류금지통장",
        "prompt": "A relieved young Korean office worker holding a bank savings book safe from seizure with a witty smirk, retro sunglasses and cap, vintage comic"
    },
    {
        "id": "6012429626510079641",
        "title": "전세사기 HUG 보증보험 이행청구 거절? 이의신청으로 2억 보증금 전액 회수",
        "prompt": "A determined everyday person holding a successful HUG deposit insurance recovery document, retro sunglasses, victorious smirk, vintage pop art"
    },
    {
        "id": "7539051147112396528",
        "title": "보이스피싱 전달책 연루, 1,500만원 입금받고 '무혐의 불송치' 받아낸 실제 증거 제출법",
        "prompt": "A relieved young person holding police non-indictment clearance paper outside police station, cool sunglasses and cap, vintage comic illustration"
    },
    {
        "id": "4194783236714087277",
        "title": "통신연체로 휴대폰 정지, 본인인증 막혔을 때 선불폰으로 10분 만에 해결",
        "prompt": "A stylish young person successfully authenticating smartphone with a prepaid USIM card, cool sunglasses and cap, vintage instatoon"
    },
    {
        "id": "3509251404438936786",
        "title": "임차권등기명령 비용 40만원으로 해결? 집주인 연락두절 시 공시송달",
        "prompt": "A relieved tenant holding apartment keys and legal leasehold registration court order, retro sunglasses and baseball cap, vintage pop art"
    },
    {
        "id": "5811603683509470669",
        "title": "불법 대부업체 연 1000% 금리 협박, 금감원 신고로 채무 전액 소멸",
        "prompt": "A cool confident person shredding illegal loan contract paper with a victorious smirk, retro sunglasses and cap, vintage comic pop art"
    }
]

JP_POSTS_TO_FIX = [
    {
        "id": "6764308500479066245",
        "title": "【体験談】賃貸退去時のクロス張替え15万円請求を「ガイドライン」提示で0円にした全手順",
        "prompt": "A confident young Japanese tenant holding rental apartment moving-out contract with a triumphant smile, retro sunglasses and cap, vintage 2D manga pop art"
    }
]


def clean_old_image_tags(content: str) -> str:
    """Remove existing external/broken img divs from HTML content."""
    # Remove div containers containing non-base64 img tags
    content = re.sub(
        r'<div style="text-align:\s*center;[^"]*">\s*<img [^>]*src=[\'"](?!data:image)[^\'"]+[\'"][^>]*>\s*(?:<p[^>]*>.*?</p>)?\s*</div>',
        '',
        content,
        flags=re.DOTALL | re.IGNORECASE
    )
    # Also strip any standalone non-base64 img tags
    content = re.sub(
        r'<img [^>]*src=[\'"](?!data:image)[^\'"]+[\'"][^>]*>',
        '',
        content,
        flags=re.IGNORECASE
    )
    return content.strip()


def fix_posts():
    c = json.load(open('blogger_credentials.json'))
    service = get_blogger_service(c)

    # 1. Clean up duplicate empty post on JP blog
    try:
        print("\n🗑️ [JP 블로그] 제목 없는 중복 테스트 글(196984568861468378) 삭제 중...")
        service.posts().delete(blogId=BLOG_ID_JP, postId='196984568861468378').execute()
        print("✅ 중복 글 삭제 완료!")
    except Exception as e:
        print(f"ℹ️ 중복 글 삭제 건너뜀/이미 삭제됨: {e}")

    # 2. Fix KR Posts
    print(f"\n🚀 [KR 블로그] 액박/외부링크 포스팅 {len(KR_POSTS_TO_FIX)}개 복구 시작...")
    for i, item in enumerate(KR_POSTS_TO_FIX, 1):
        pid = item["id"]
        print(f"\n[{i}/{len(KR_POSTS_TO_FIX)}] 포스트 ID: {pid} | {item['title'][:30]}...")
        try:
            p = service.posts().get(blogId=BLOG_ID_KR, postId=pid).execute()
            old_content = p.get('content', '')

            # Generate new 2D retro instatoon image
            img_bytes = fetch_flux_image_bytes(item["prompt"])
            if not img_bytes:
                print(f"❌ 이미지 생성 실패: {pid}")
                continue

            b64_str = base64.b64encode(img_bytes).decode('utf-8')
            banner_html = (
                f'<div style="text-align: center; margin: 30px auto; max-width: 720px;">\n'
                f'  <img src="data:image/jpeg;base64,{b64_str}" alt="{item["title"]}" '
                f'style="width: 100%; height: auto; border-radius: 12px; box-shadow: 0 4px 16px rgba(0,0,0,0.12);" />\n'
                f'  <p style="color: #777; font-size: 13px; margin-top: 8px; text-align: center;">▲ {item["title"][:30]}... (2D 레트로 인스타툰 일러스트)</p>\n'
                f'</div>\n'
            )

            cleaned_content = clean_old_image_tags(old_content)
            new_content = banner_html + cleaned_content

            service.posts().patch(
                blogId=BLOG_ID_KR,
                postId=pid,
                body={'content': new_content}
            ).execute()
            print(f"🎉 [성공] 포스트 '{item['title'][:25]}'에 2D 레트로 인스타툰 Base64 이미지 교체 완료!")

            # 10s cooldown for Pollinations queue
            print("⏳ 다음 이미지 생성을 위해 10초 대기 중...")
            time.sleep(10)

        except Exception as e:
            print(f"❌ 포스트 업데이트 실패: {e}")

    # 3. Fix JP Post
    print(f"\n🚀 [JP 블로그] 외부링크 포스팅 {len(JP_POSTS_TO_FIX)}개 복구 시작...")
    for i, item in enumerate(JP_POSTS_TO_FIX, 1):
        pid = item["id"]
        print(f"\n[{i}/{len(JP_POSTS_TO_FIX)}] 포스트 ID: {pid} | {item['title'][:30]}...")
        try:
            p = service.posts().get(blogId=BLOG_ID_JP, postId=pid).execute()
            old_content = p.get('content', '')

            img_bytes = fetch_flux_image_bytes(item["prompt"])
            if not img_bytes:
                print(f"❌ 이미지 생성 실패: {pid}")
                continue

            b64_str = base64.b64encode(img_bytes).decode('utf-8')
            banner_html = (
                f'<div style="text-align: center; margin: 30px auto; max-width: 720px;">\n'
                f'  <img src="data:image/jpeg;base64,{b64_str}" alt="{item["title"]}" '
                f'style="width: 100%; height: auto; border-radius: 12px; box-shadow: 0 4px 16px rgba(0,0,0,0.12);" />\n'
                f'  <p style="color: #777; font-size: 13px; margin-top: 8px; text-align: center;">▲ {item["title"][:30]}... (2Dレトロポップアートイラスト)</p>\n'
                f'</div>\n'
            )

            cleaned_content = clean_old_image_tags(old_content)
            new_content = banner_html + cleaned_content

            service.posts().patch(
                blogId=BLOG_ID_JP,
                postId=pid,
                body={'content': new_content}
            ).execute()
            print(f"🎉 [성공] 일본 포스트 '{item['title'][:25]}'에 2D 레트로 인스타툰 Base64 이미지 교체 완료!")

        except Exception as e:
            print(f"❌ 일본 포스트 업데이트 실패: {e}")

    print("\n🏁 모든 액박 및 과거 포스팅의 이미지 복구 작업이 완료되었습니다!")


if __name__ == '__main__':
    fix_posts()
