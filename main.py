"""
Main CLI Runner for kgamjablog.blogspot.com
Includes AI Article Writing, Photorealistic FLUX Image Generation, and Google Blogger Email Auto-Posting.
"""
import sys
import os
import json
import argparse

# Reconfigure stdout for Windows console UTF-8 support
sys.stdout.reconfigure(encoding='utf-8')

from article_generator import generate_article
from image_manager_flux import generate_flux_image_url, insert_flux_image_into_content
from blogger_email_client import send_post_via_email
from config import SMTP_USER, SMTP_PASSWORD, BLOGGER_EMAIL, BLOG_URL

QUEUE_FILE = "topics_queue.json"


def load_queue():
    if not os.path.exists(QUEUE_FILE):
        return []
    with open(QUEUE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_queue(queue):
    with open(QUEUE_FILE, "w", encoding="utf-8") as f:
        json.dump(queue, f, ensure_ascii=False, indent=2)


def process_topic(topic: str):
    print(f"\n🚀 [1/3] AI 글 및 실사 이미지 기획 시작: '{topic}'")
    print("⏳ Gemini 모델로 1인칭 공감형 칼럼, 구글 SEO 최적화 본문, 실사 사진 프롬프트 생성 중...")
    
    article = generate_article(topic)
    
    title = article.get("title", topic)
    category = article.get("category", "생활법률")
    excerpt = article.get("excerpt", "")
    tags = article.get("tags", [])
    if category not in tags:
        tags.insert(0, category)

    image_prompt_en = article.get("image_prompt_en", f"realistic scene about {topic}")
    content_html = article.get("content_html", "")

    print(f"\n✅ [글 생성 완료]")
    print(f"📌 제목: {title}")
    print(f"📂 카테고리: {category}")
    print(f"🏷️  태그: {', '.join(tags)}")
    print(f"📝 메타 요약 ({len(excerpt)}자): {excerpt}")
    print(f"📊 본문 글자 수: {len(content_html)} 글자")

    # 2. Generate Photorealistic FLUX Image
    print(f"\n🚀 [2/3] Gemini 아트 디렉터 + FLUX 실사 고화질 사진 생성 중...")
    flux_image_url = generate_flux_image_url(image_prompt_en)
    print(f"📸 FLUX 실사 이미지 URL 생성 완료: {flux_image_url[:90]}...")

    # Embed photorealistic image into the article content
    content_html = insert_flux_image_into_content(
        content_html=content_html,
        image_url=flux_image_url,
        alt_text=f"{title} 관련 실사 안내 사진"
    )

    # 3. Publish to Google Blogger via Email
    print(f"\n🚀 [3/3] 구글 블로거로 자동 발행 전송 중 ({BLOGGER_EMAIL})...")
    result = send_post_via_email(
        title=title,
        content_html=content_html,
        tags=tags,
        smtp_user=SMTP_USER,
        smtp_password=SMTP_PASSWORD
    )

    if result.get("success"):
        print(f"\n🎉 [발행 성공] 구글 블로거로 글이 정상 전송되었습니다!")
        print(f"🌐 블로그 주소: {BLOG_URL}")
        print(f"📌 발행된 글 제목: {title}")
    else:
        print(f"⚠️ 발행 실패: {result.get('error')}")

    return result


def main():
    parser = argparse.ArgumentParser(description="kgamjablog 구글 블로거 자동 포스팅 도구")
    parser.add_argument("--topic", "-t", type=str, help="작성할 주제 직접 입력")
    parser.add_argument("--next", "-n", action="store_true", help="큐에서 다음 추천 키워드 자동 실행")
    parser.add_argument("--list", "-l", action="store_true", help="추천 키워드 큐 목록 조회")

    args = parser.parse_args()

    if args.list:
        queue = load_queue()
        print("\n📋 [추천 키워드 큐 목록]")
        for i, item in enumerate(queue, 1):
            st = "✅ 완료" if item.get("status") == "done" else "⏳ 대기"
            print(f"{i:02d}. [{st}] [{item.get('category')}] {item.get('topic')}")
        return

    if args.next:
        queue = load_queue()
        pending = [q for q in queue if q.get("status") != "done"]
        if not pending:
            print("⚠️ 큐에 대기 중인 키워드가 없습니다.")
            return
        item = pending[0]
        result = process_topic(item["topic"])
        if result.get("success"):
            item["status"] = "done"
            save_queue(queue)
        return

    if args.topic:
        process_topic(args.topic)
        return

    parser.print_help()


if __name__ == "__main__":
    main()
