"""
Main CLI Runner for Japanese Blog: 暮らしの法律とお金の知恵
Publishes high-CPC Japanese legal/finance articles with 2D manga comic art to dlwoduq20.jp2026@blogger.com.
"""
import sys
import os
import json
import argparse

# Reconfigure stdout for Windows console UTF-8 support
sys.stdout.reconfigure(encoding='utf-8')

from article_generator_jp import generate_article_jp
from image_manager_flux import fetch_flux_image_bytes
from blogger_client import publish_blogger_post, BLOG_ID_JP

QUEUE_FILE_JP = "topics_queue_jp.json"
BLOG_URL_JP = "https://seikatsulaw.blogspot.com"


def load_queue_jp():
    if not os.path.exists(QUEUE_FILE_JP):
        return []
    with open(QUEUE_FILE_JP, "r", encoding="utf-8") as f:
        return json.load(f)


def save_queue_jp(queue):
    with open(QUEUE_FILE_JP, "w", encoding="utf-8") as f:
        json.dump(queue, f, ensure_ascii=False, indent=2)


def process_topic_jp(topic: str):
    print(f"\n🇯🇵 [1/3] 日本語記事＆マンガ画像企画開始: '{topic}'")
    print("⏳ Geminiモデルで一人称体験談、Google Japan SEO最適化本文、2Dマンガプロンプトを生成中...")
    
    article = generate_article_jp(topic)
    
    title = article.get("title", topic)
    category = article.get("category", "暮らしの法律")
    excerpt = article.get("excerpt", "")
    tags = article.get("tags", [])
    if category not in tags:
        tags.insert(0, category)

    image_prompt_en = article.get("image_prompt_en", f"Japanese anime drawing about {topic}")
    content_html = article.get("content_html", "")

    print(f"\n✅ [記事生成完了]")
    print(f"📌 タイトル: {title}")
    print(f"📂 カテゴリ: {category}")
    print(f"🏷️  タグ: {', '.join(tags)}")
    print(f"📝 メタ要約 ({len(excerpt)}文字): {excerpt}")
    print(f"📊 本文文字数: {len(content_html)} 文字")

    # 2. Fetch 2D Manga Illustration Bytes
    print(f"\n🚀 [2/3] 2Dマンガスタイルイラスト生成＆ダウンロード中...")
    image_bytes = fetch_flux_image_bytes(image_prompt_en)

    # 3. Publish to Japanese Blogger via official REST API v3
    print(f"\n🚀 [3/3] Google Blogger 公式 REST API v3で記事＆2Dマンガイラストを直接投稿中...")
    result = publish_blogger_post(
        title=title,
        content_html=content_html,
        labels=tags,
        image_bytes=image_bytes,
        blog_id=BLOG_ID_JP
    )

    if result.get("success"):
        print(f"\n🎉 [投稿成功] 日本のブログへ記事が正常に公開されました！")
        print(f"🌐 ブログURL: {BLOG_URL_JP}")
        print(f"📌 記事URL: {result.get('post_url')}")
        print(f"📌 タイトル: {title}")
    else:
        print(f"⚠️ 投稿失敗: {result.get('error')}")

    return result


def main():
    parser = argparse.ArgumentParser(description="Japanese Blogger Auto Posting CLI")
    parser.add_argument("--topic", "-t", type=str, help="執筆するテーマを直接入力")
    parser.add_argument("--next", "-n", action="store_true", help="キューから次の記事を自動実行")
    parser.add_argument("--list", "-l", action="store_true", help="記事キュー一覧を表示")

    args = parser.parse_args()

    if args.list:
        queue = load_queue_jp()
        print("\n📋 [日本語ブログ記事キュー一覧]")
        for i, item in enumerate(queue, 1):
            st = "✅ 完了" if item.get("status") == "done" else "⏳ 待機"
            print(f"{i:02d}. [{st}] [{item.get('category')}] {item.get('topic')}")
        return

    if args.next:
        queue = load_queue_jp()
        pending = [q for q in queue if q.get("status") != "done"]
        if not pending:
            print("⚠️ キューに待機中の記事がありません。")
            return
        item = pending[0]
        result = process_topic_jp(item["topic"])
        if result.get("success"):
            item["status"] = "done"
            save_queue_jp(queue)
        return

    if args.topic:
        process_topic_jp(args.topic)
        return

    parser.print_help()


if __name__ == "__main__":
    main()
