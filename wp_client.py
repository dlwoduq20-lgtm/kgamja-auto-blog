"""
WordPress REST API Client
"""
import os
import requests
from config import WP_URL, WP_USER, WP_APP_PASSWORD, CATEGORY_MAP


def publish_post(
    title: str,
    content: str,
    excerpt: str,
    category_name: str,
    tags: list,
    slug: str = None,
    featured_media_id: int = None,
    status: str = "draft"
) -> dict:
    """
    Publish or create a draft post to WordPress via REST API.
    Includes slug, featured image, meta description, and category mapping.
    """
    category_id = CATEGORY_MAP.get(category_name, None)
    
    # Save locally to output folder
    os.makedirs("output", exist_ok=True)
    safe_filename = "".join([c for c in title if c.isalnum() or c in (' ', '_', '-')]).strip()[:50]
    local_path = os.path.join("output", f"{safe_filename}.html")
    
    with open(local_path, "w", encoding="utf-8") as f:
        f.write(f"<!--\nTitle: {title}\nSlug: {slug}\nCategory: {category_name}\nTags: {', '.join(tags)}\nExcerpt: {excerpt}\nFeatured Media ID: {featured_media_id}\n-->\n\n{content}")
    
    print(f"📁 Local backup saved to: {local_path}")

    # If WordPress credentials are not set, return local save result
    if not WP_USER or not WP_APP_PASSWORD:
        return {
            "success": True,
            "mode": "local_file",
            "file_path": local_path,
            "message": "WordPress credentials not provided. Post saved locally."
        }

    # Post to WordPress REST API
    api_url = f"{WP_URL.rstrip('/')}/wp-json/wp/v2/posts"
    auth = (WP_USER, WP_APP_PASSWORD)
    
    payload = {
        "title": title,
        "content": content,
        "excerpt": excerpt,
        "status": status,  # "draft" or "publish"
        "meta": {
            "_yoast_wpseo_metadesc": excerpt,
            "_yoast_wpseo_title": f"{title} | 생활 속 법과 금융",
            "description": excerpt
        }
    }

    if slug:
        payload["slug"] = slug

    if category_id:
        payload["categories"] = [category_id]

    if featured_media_id:
        payload["featured_media"] = featured_media_id

    try:
        response = requests.post(api_url, auth=auth, json=payload, timeout=30)
        if response.status_code in (200, 201):
            data = response.json()
            post_id = data.get("id")
            post_link = data.get("link")
            post_slug = data.get("slug")
            return {
                "success": True,
                "mode": "wordpress_api",
                "post_id": post_id,
                "post_link": post_link,
                "post_slug": post_slug,
                "featured_media": data.get("featured_media"),
                "status": status,
                "file_path": local_path
            }
        else:
            return {
                "success": False,
                "error": f"WordPress API error ({response.status_code}): {response.text}",
                "file_path": local_path
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "file_path": local_path
        }
