"""
Main CLI Runner for kgamjablog.blogspot.com
Includes AI Article Writing, Photorealistic FLUX Image Generation, and Google Blogger Email Auto-Posting with Attached Images.
"""
import sys
import os
import json
import argparse

# Reconfigure stdout for Windows console UTF-8 support
sys.stdout.reconfigure(encoding='utf-8')

from article_generator import generate_article
from image_manager_chatgpt import fetch_chatgpt_thumbnail_bytes
from blogger_client import publish_blogger_post, BLOG_ID_KR
from config import BLOG_URL

QUEUE_FILE = "topics_queue.json"


def load_queue():
    if not os.path.exists(QUEUE_FILE):
        return []
    with open(QUEUE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_queue(queue):
    with open(QUEUE_FILE, "w", encoding="utf-8") as f:
        json.dump(queue, f, ensure_ascii=False, indent=2)


def get_related_kr_articles(current_topic: str = "") -> list:
    """
    Fetch published posts from Blogger API to find related articles for contextual internal linking.
    """
    try:
        from blogger_client import get_blogger_service
        if os.path.exists("blogger_credentials.json"):
            with open("blogger_credentials.json", "r", encoding="utf-8") as f:
                c = json.load(f)
            service = get_blogger_service(c)
            posts = service.posts().list(blogId=BLOG_ID_KR, maxResults=20).execute().get("items", [])
            candidates = []
            for p in posts:
                t = p.get("title", "")
                u = p.get("url", "")
                if u and t and t.lower() != current_topic.lower():
                    candidates.append({"title": t, "url": u})
            return candidates[:3]
    except Exception as e:
        print(f"ℹ️ [내부 링크] 후보 글 조회 참고: {e}")
    return []


def process_topic(topic: str):
    print(f"\n🚀 [1/3] AI 글 및 2D 웹툰 일러스트 기획 시작: '{topic}'")
    
    related = get_related_kr_articles(current_topic=topic)
    if related:
        print(f"🔗 [내부 링크] 맥락형 내부 링크 후보 {len(related)}개 연동:")
        for r in related:
            print(f"   - {r['title']}")

    print("⏳ Gemini 모델로 1인칭 공감형 칼럼, E-E-A-T 준칙, 동적 소제목, 2D 웹툰 만화 프롬프트 생성 중...")
    article = generate_article(topic, related_articles=related)
    
    title = article.get("title", topic)
    category = article.get("category", "생활법률")
    excerpt = article.get("excerpt", "")
    tags = article.get("tags", [])
    if category not in tags:
        tags.insert(0, category)

    image_prompt_en = article.get("image_prompt_en", f"Korean webtoon style 2D drawing about {topic}")
    content_html = article.get("content_html", "")

    print(f"\n✅ [글 생성 완료]")
    print(f"📌 제목: {title}")
    print(f"📂 카테고리: {category}")
    print(f"🏷️  태그: {', '.join(tags)}")
    print(f"📝 메타 요약 ({len(excerpt)}자): {excerpt}")
    print(f"📊 본문 글자 수: {len(content_html)} 글자")

    # 2. Fetch 3D Card-News Thumbnail Bytes (ChatGPT DALL-E / 3D Style)
    print(f"\n🚀 [2/3] 챗GPT 스타일 3D 카드뉴스 썸네일 생성 중...")
    image_bytes = fetch_chatgpt_thumbnail_bytes(title, language="ko", category=category)

    # Google SEO JSON-LD Schema Markup (BlogPosting & FAQPage)
    schema_entities = [
        {
            "@context": "https://schema.org",
            "@type": "BlogPosting",
            "headline": title,
            "description": excerpt,
            "articleSection": category,
            "keywords": tags,
            "inLanguage": "ko",
            "mainEntityOfPage": {"@type": "WebPage"}
        }
    ]
    if article.get("faq_schema"):
        schema_entities.append({
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": [
                {
                    "@type": "Question",
                    "name": item.get("question"),
                    "acceptedAnswer": {
                        "@type": "Answer",
                        "text": item.get("answer")
                    }
                }
                for item in article["faq_schema"] if item.get("question") and item.get("answer")
            ]
        })

    for s in schema_entities:
        content_html += f"\n<script type=\"application/ld+json\">\n{json.dumps(s, ensure_ascii=False, indent=2)}\n</script>\n"

    # 3. Publish to Google Blogger via official REST API v3
    print(f"\n🚀 [3/3] 구글 블로거 공식 REST API v3로 글 및 2D 웹툰 일러스트 즉시 등록 중...")
    result = publish_blogger_post(
        title=title,
        content_html=content_html,
        labels=tags,
        image_bytes=image_bytes,
        blog_id=BLOG_ID_KR
    )

    if result.get("success"):
        print(f"\n🎉 [발행 성공] 구글 블로거로 글과 2D 웹툰 일러스트가 정상 발행되었습니다!")
        print(f"🌐 블로그 주소: {BLOG_URL}")
        print(f"📌 포스팅 URL: {result.get('post_url')}")
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
