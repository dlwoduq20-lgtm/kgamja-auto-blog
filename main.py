"""
Main CLI Runner for kgamjablog.blog automation
Includes AI Article Writing, SEO Meta Description, Topic-Accurate Featured Image, In-Content Image, and English Kebab-Case Slug.
"""
import sys
import os
import json
import argparse

# Reconfigure stdout for Windows console UTF-8 support
sys.stdout.reconfigure(encoding='utf-8')

from article_generator import generate_article
from wp_client import publish_post
from image_manager import generate_and_upload_post_image, insert_image_into_content

QUEUE_FILE = "topics_queue.json"


def load_queue():
    if not os.path.exists(QUEUE_FILE):
        return []
    with open(QUEUE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_queue(queue):
    with open(QUEUE_FILE, "w", encoding="utf-8") as f:
        json.dump(queue, f, ensure_ascii=False, indent=2)


def process_topic(topic: str, status: str = "draft"):
    print(f"\n🚀 [1/3] AI 글 및 메타 데이터 생성 시작: '{topic}'")
    print("⏳ Gemini 모델로 1인칭 공감형 글, 150자 SEO 메타 디스크립션, 영문 슬러그 생성 중...")
    
    article = generate_article(topic)
    
    title = article.get("title", topic)
    slug = article.get("slug", "")
    category = article.get("category", "생활법률")
    excerpt = article.get("excerpt", "")
    tags = article.get("tags", [])
    image_prompt_en = article.get("image_prompt_en", f"illustration about {topic}")
    content_html = article.get("content_html", "")

    print(f"\n✅ [글 생성 완료]")
    print(f"📌 제목: {title}")
    print(f"🔤 슬러그(URL): {slug}")
    print(f"📂 카테고리: {category}")
    print(f"🏷️  태그: {', '.join(tags)}")
    print(f"📝 메타 디스크립션 ({len(excerpt)}자): {excerpt}")
    print(f"🎨 이미지 프롬프트: {image_prompt_en}")
    print(f"📊 글자 수: {len(content_html)} 글자")

    # 2. Generate and upload topic-accurate image
    print(f"\n🚀 [2/3] 주제 맞춤형 AI 이미지 생성 및 워드프레스 업로드...")
    img_res = generate_and_upload_post_image(topic, image_prompt_en)
    
    featured_media_id = None
    if img_res:
        featured_media_id = img_res.get("media_id")
        image_url = img_res.get("source_url")
        # Embed image into the article content
        content_html = insert_image_into_content(
            content_html=content_html,
            image_url=image_url,
            alt_text=f"{title} 설명 이미지"
        )
        print(f"🖼️  본문 내 이미지 삽입 완료: {image_url}")

    # 3. Publish to WordPress
    print(f"\n🚀 [3/3] 워드프레스 발행 처리 중 (상태: {status})...")
    result = publish_post(
        title=title,
        content=content_html,
        excerpt=excerpt,
        category_name=category,
        tags=tags,
        slug=slug,
        featured_media_id=featured_media_id,
        status=status
    )

    if result.get("success"):
        if result.get("mode") == "wordpress_api":
            print(f"\n🎉 워드프레스 포스팅 성공!")
            print(f"🆔 Post ID: {result.get('post_id')}")
            print(f"🔗 글 링크: {result.get('post_link')}")
            print(f"🔤 적용된 슬러그: {result.get('post_slug')}")
            print(f"🖼️  대표 이미지 ID: {result.get('featured_media')}")
            print(f"📝 메타 디스크립션 설정 완료 ({len(excerpt)}자)")
        else:
            print(f"💾 로컬 파일 저장 완료: {result.get('file_path')}")
    else:
        print(f"⚠️ 발행 실패: {result.get('error')}")

    return result


def main():
    parser = argparse.ArgumentParser(description="kgamjablog.blog 자동 포스팅 도구")
    parser.add_argument("--topic", "-t", type=str, help="작성할 주제/키워드 직접 입력")
    parser.add_argument("--next", "-n", action="store_true", help="큐에서 다음 추천 키워드 자동 실행")
    parser.add_argument("--list", "-l", action="store_true", help="추천 키워드 큐 목록 조회")
    parser.add_argument("--status", "-s", choices=["draft", "publish"], default="draft", help="발행 상태 (기본값: draft)")

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
        result = process_topic(item["topic"], status=args.status)
        if result.get("success"):
            item["status"] = "done"
            save_queue(queue)
        return

    if args.topic:
        process_topic(args.topic, status=args.status)
        return

    parser.print_help()


if __name__ == "__main__":
    main()
