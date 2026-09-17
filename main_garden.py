'''
Main CLI Runner for Home & Garden (Horticulture & Small-Scale Agriculture) Blog
Publishes deep, zone-specific gardening guides with pastoral pastel vector illustrations to Google Blogger.
'''
import sys
import os
import json
import argparse

# Force UTF-8 on Windows consoles
sys.stdout.reconfigure(encoding='utf-8')

from article_generator_garden import generate_article_garden
from blogger_client import publish_blogger_post

QUEUE_FILE_GARDEN = "topics_queue_garden.json"
DEFAULT_BLOG_ID_GARDEN = "7758791627533733698"
BLOG_ID_GARDEN = os.environ.get("BLOG_ID_GARDEN", DEFAULT_BLOG_ID_GARDEN)
BLOG_URL_GARDEN = "https://greenthumb-garden.blogspot.com"


def load_queue_garden():
    if not os.path.exists(QUEUE_FILE_GARDEN):
        return []
    with open(QUEUE_FILE_GARDEN, "r", encoding="utf-8") as f:
        return json.load(f)


def save_queue_garden(queue):
    with open(QUEUE_FILE_GARDEN, "w", encoding="utf-8") as f:
        json.dump(queue, f, ensure_ascii=False, indent=2)


def get_avoid_topics(queue):
    return [q.get("keyword") for q in queue if q.get("status") == "done"]


def get_related_garden_articles(current_keyword: str = "") -> list:
    """
    Fetch published posts from Blogger API to find related articles for contextual internal linking.
    """
    try:
        from blogger_client import get_blogger_service
        if os.path.exists("blogger_credentials.json"):
            with open("blogger_credentials.json", "r", encoding="utf-8") as f:
                c = json.load(f)
            service = get_blogger_service(c)
            posts = service.posts().list(blogId=BLOG_ID_GARDEN, maxResults=20).execute().get("items", [])
            candidates = []
            for p in posts:
                t = p.get("title", "")
                u = p.get("url", "")
                if u and t and t.lower() != current_keyword.lower():
                    candidates.append({"title": t, "url": u})
            return candidates[:3]
    except Exception as e:
        print(f"ℹ️ [Internal Linking] Candidate fetch notice: {e}")
    return []


def process_topic_garden(keyword: str, topic_angle: str = "", queue=None):
    print(f"\n🌱 [1/3] AI Home & Garden Article Writing Started: '{keyword}'")
    
    related = get_related_garden_articles(current_keyword=keyword)
    if related:
        print(f"🔗 [Internal Linking] Connecting {len(related)} contextual internal guides:")
        for r in related:
            print(f"   - {r['title']}")

    print(f"⏳ Generating E-E-A-T rich horticulture guide with dynamic headings & pastel vector illustrations...")

    avoid_list = get_avoid_topics(queue) if queue else []
    article = generate_article_garden(
        keyword=keyword,
        topic_angle=topic_angle,
        avoid_topics=avoid_list,
        related_articles=related
    )

    h1 = article.get("h1", keyword)
    meta_title = article.get("meta_title", h1)
    meta_description = article.get("meta_description", "")
    category = article.get("category", "Home & Garden")
    tags = article.get("tags", [])
    if category not in tags:
        tags.insert(0, category)
    slug = article.get("url_slug", "")
    content_html = article.get("content_html", "")

    print(f"\n✅ [Article Generation Completed]")
    print(f"📌 H1 Title: {h1}")
    print(f"🏷️  Meta Title: {meta_title}")
    print(f"📂 Category: {category}")
    print(f"🏷️  Tags: {', '.join(tags)}")
    print(f"🔗 Slug: {slug}")
    print(f"📝 Meta Description ({len(meta_description)} chars): {meta_description}")
    print(f"📊 Content Length: {len(content_html)} characters")

    # 2. Publish to Blogger via official REST API v3
    print(f"\n🚀 [2/3] Publishing to Google Blogger (Blog ID: {BLOG_ID_GARDEN})...")
    result = publish_blogger_post(
        title=h1,
        content_html=content_html,
        labels=tags,
        image_bytes=None,  # Base64 images are already embedded into content_html
        blog_id=BLOG_ID_GARDEN
    )

    if result.get("success"):
        print(f"\n🎉 [Publish Success] Home & Garden article successfully published!")
        print(f"🌐 Blog URL: {BLOG_URL_GARDEN}")
        print(f"📌 Post URL: {result.get('post_url')}")
        print(f"📌 Post Title: {h1}")
    else:
        print(f"⚠️ Publish Failed: {result.get('error')}")

    return result


def main():
    parser = argparse.ArgumentParser(description="Home & Garden Blogger Auto-Publishing CLI")
    parser.add_argument("--keyword", "-k", type=str, help="Target primary keyword directly")
    parser.add_argument("--topic", "-t", type=str, default="", help="Specific topic or angle")
    parser.add_argument("--next", "-n", action="store_true", help="Automatically process next pending keyword from queue")
    parser.add_argument("--list", "-l", action="store_true", help="List keywords in garden queue")

    args = parser.parse_args()

    if args.list:
        queue = load_queue_garden()
        print(f"\n📋 [Home & Garden Queue ({len(queue)} topics)]")
        for i, item in enumerate(queue, 1):
            st = "✅ Done" if item.get("status") == "done" else "⏳ Pending"
            print(f"{i:02d}. [{st}] [{item.get('season')}] [{item.get('category')}] {item.get('keyword')}")
        return

    if args.next:
        queue = load_queue_garden()
        pending = [q for q in queue if q.get("status") != "done"]
        if not pending:
            print("⚠️ No pending topics found in garden queue.")
            return
        item = pending[0]
        result = process_topic_garden(item["keyword"], item.get("topic", ""), queue)
        if result.get("success"):
            item["status"] = "done"
            item["post_url"] = result.get("post_url")
            save_queue_garden(queue)
        return

    if args.keyword:
        queue = load_queue_garden()
        result = process_topic_garden(args.keyword, args.topic, queue)
        if result.get("success"):
            # Mark as done if in queue
            for q in queue:
                if q.get("keyword").lower() == args.keyword.lower():
                    q["status"] = "done"
                    q["post_url"] = result.get("post_url")
            save_queue_garden(queue)
        return

    parser.print_help()


if __name__ == "__main__":
    main()
