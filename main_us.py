'''
Main CLI Runner for US/Global B2B SaaS Software Review & Comparison Blog
Publishes deep, high-converting buyer guides with modern 2D tech graphics via Google Blogger API v3.
'''
import sys
import os
import json
import argparse

sys.stdout.reconfigure(encoding='utf-8')

from article_generator_saas import generate_article_saas
from image_manager_saas import fetch_saas_image_bytes
from blogger_client import publish_blogger_post

QUEUE_FILE_US = "topics_queue_us.json"
DEFAULT_BLOG_ID_US = "1939932974175805877"
BLOG_ID_US = os.environ.get("BLOG_ID_US", DEFAULT_BLOG_ID_US)


def load_queue_us():
    if not os.path.exists(QUEUE_FILE_US):
        return []
    with open(QUEUE_FILE_US, "r", encoding="utf-8") as f:
        return json.load(f)


def save_queue_us(queue):
    with open(QUEUE_FILE_US, "w", encoding="utf-8") as f:
        json.dump(queue, f, ensure_ascii=False, indent=2)


def process_topic_us(item: dict):
    keyword = item.get("keyword", item.get("topic"))
    topic = item.get("topic", keyword)
    category = item.get("category", "SaaS Reviews")
    
    print(f"\n🇺🇸 [1/3] Planning B2B SaaS Review Article: '{topic}'")
    print(f"⏳ Generating in-depth buyer guide, comparison table, pricing analysis, and 2D vector prompt...")
    
    article = generate_article_saas(keyword=keyword, topic_angle=topic)
    
    title = article.get("h1", article.get("meta_title", topic))
    content_html = article.get("content_html", "")
    tags = article.get("tags", [category, "SaaS", "Software Review", "B2B Tools"])
    if category not in tags:
        tags.insert(0, category)
        
    excerpt = article.get("meta_description", "")
    image_prompt_en = article.get("image_prompt_en", f"modern tech illustration representing {keyword}")

    print(f"\n✅ [Article Generation Complete]")
    print(f"📌 Title: {title}")
    print(f"📂 Category: {category}")
    print(f"🏷️  Tags: {', '.join(tags)}")
    print(f"📝 Meta Description ({len(excerpt)} chars): {excerpt}")
    print(f"📊 Content Length: {len(content_html)} characters")

    # 2. Fetch 2D Tech Illustration Bytes
    print(f"\n🚀 [2/3] Generating modern 2D vector tech illustration via FLUX...")
    image_bytes = fetch_saas_image_bytes(image_prompt_en)

    # 3. Publish to US Blogger via official REST API v3
    print(f"\n🚀 [3/3] Publishing to US Google Blogger via official REST API v3 (Blog ID: {BLOG_ID_US})...")
    result = publish_blogger_post(
        title=title,
        content_html=content_html,
        labels=tags,
        image_bytes=image_bytes,
        blog_id=BLOG_ID_US
    )

    if result.get("success"):
        print(f"\n🎉 [Publish Success] B2B SaaS review published live on Google Blogger!")
        print(f"📌 Post URL: {result.get('post_url')}")
        print(f"📌 Title: {title}")
    else:
        print(f"⚠️ Publish failed: {result.get('error')}")

    return result


def main():
    parser = argparse.ArgumentParser(description="US B2B SaaS Blogger Auto Posting CLI")
    parser.add_argument("--keyword", "-k", type=str, help="Primary target keyword")
    parser.add_argument("--next", "-n", action="store_true", help="Run next pending topic from queue")
    parser.add_argument("--list", "-l", action="store_true", help="Display pending topic queue")

    args = parser.parse_args()

    if args.list:
        queue = load_queue_us()
        print("\n📋 [US B2B SaaS Topic Queue]")
        for i, item in enumerate(queue, 1):
            st = "✅ Done" if item.get("status") == "done" else "⏳ Pending"
            print(f"{i:02d}. [{st}] [{item.get('category')}] {item.get('topic')}")
        return

    if args.next:
        queue = load_queue_us()
        pending = [q for q in queue if q.get("status") != "done"]
        if not pending:
            print("⚠️ No pending topics in queue.")
            return
        item = pending[0]
        result = process_topic_us(item)
        if result.get("success"):
            item["status"] = "done"
            save_queue_us(queue)
        return

    if args.keyword:
        process_topic_us({"keyword": args.keyword, "topic": args.keyword, "category": "SaaS Reviews"})
        return

    parser.print_help()


if __name__ == "__main__":
    main()
