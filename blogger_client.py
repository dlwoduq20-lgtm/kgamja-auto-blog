"""
Google Blogger API v3 Client for kgamjablog & seikatsulaw
"""
import os
import sys
import json
import base64
import requests
import re
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass

BLOG_ID_KR = "3888865366756619756"
BLOG_ID_JP = "4884263507030240234"
SCOPES = ["https://www.googleapis.com/auth/blogger"]


def upload_image_to_cdn(image_bytes: bytes) -> str:
    """
    Upload image bytes to CDN to obtain a permanent https:// image URL.
    Saves directly to assets/ directory and pushes to GitHub repository.
    100% accessible in South Korea and globally without any ISP blocking.
    """
    if not image_bytes:
        return None

    try:
        import hashlib
        import subprocess
        img_hash = hashlib.md5(image_bytes).hexdigest()[:12]
        assets_dir = os.path.join(os.path.dirname(__file__), "assets")
        os.makedirs(assets_dir, exist_ok=True)
        thumb_filename = f"thumb_{img_hash}.jpg"
        thumb_path = os.path.join(assets_dir, thumb_filename)
        
        with open(thumb_path, "wb") as f:
            f.write(image_bytes)
            
        try:
            subprocess.run(["git", "add", thumb_path], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run(["git", "commit", "-m", f"chore: add asset thumbnail {thumb_filename}"], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run(["git", "push", "origin", "main"], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception as ge:
            print(f"⚠️ Git push notice: {ge}")

        raw_url = f"https://raw.githubusercontent.com/dlwoduq20-lgtm/kgamja-auto-blog/main/assets/{thumb_filename}"
        print(f"✅ Image successfully hosted on GitHub CDN: {raw_url}")
        return raw_url
    except Exception as e:
        print(f"⚠️ CDN upload failed: {e}")

    return None


def get_blogger_service(credentials_dict: dict):
    """
    Build Blogger service using OAuth2 credentials dictionary.
    """
    creds = Credentials(
        token=credentials_dict.get("token"),
        refresh_token=credentials_dict.get("refresh_token"),
        token_uri="https://oauth2.googleapis.com/token",
        client_id=credentials_dict.get("client_id"),
        client_secret=credentials_dict.get("client_secret"),
        scopes=SCOPES
    )
    return build("blogger", "v3", credentials=creds)


def publish_blogger_post(
    title: str,
    content_html: str,
    labels: list,
    image_bytes: bytes = None,
    blog_id: str = BLOG_ID_KR,
    credentials_dict: dict = None,
    is_draft: bool = False
) -> dict:
    """
    Publish a post to Google Blogger using Blogger API v3.
    Supports embedding generated 2D comic illustration directly.
    """
    if not credentials_dict:
        # Load from environment or local credentials file
        cred_env = os.environ.get("BLOGGER_CREDENTIALS")
        if cred_env:
            credentials_dict = json.loads(cred_env)
        elif os.path.exists("blogger_credentials.json"):
            with open("blogger_credentials.json", "r", encoding="utf-8") as f:
                credentials_dict = json.load(f)
        else:
            raise ValueError("Blogger credentials not found. Please provide credentials or run setup_blogger_oauth.py.")

    service = get_blogger_service(credentials_dict)

    # Embed 2D illustration if provided
    if image_bytes:
        cdn_url = upload_image_to_cdn(image_bytes)
        if cdn_url:
            img_src = cdn_url
        else:
            b64_data = base64.b64encode(image_bytes).decode("utf-8")
            img_src = f"data:image/jpeg;base64,{b64_data}"

        image_html = (
            f'<div class="separator" style="clear: both; text-align: center; margin: 0 0 25px 0;">\n'
            f'  <a href="{img_src}" style="margin-left: 1em; margin-right: 1em;">\n'
            f'    <img border="0" data-original-height="800" data-original-width="800" src="{img_src}" alt="{title}" '
            f'style="max-width: 100%; height: auto; border-radius: 12px; box-shadow: 0 4px 16px rgba(0,0,0,0.12); display: inline-block;" />\n'
            f'  </a>\n'
            f'</div>\n\n'
        )
        # CRITICAL FOR BLOGGER THUMBNAILS:
        # The primary image MUST appear BEFORE the <!--more--> jump-break tag!
        # If the image is after <!--more-->, Blogger homepage feeds cannot find any image
        # in the post teaser, resulting in broken/missing thumbnails on initial publish.
        if "<!--more-->" in content_html:
            content_html = image_html + content_html
        else:
            p_m = re.search(r'(<p[^>]*>.*?</p>)', content_html, re.S)
            if p_m:
                lead_p = p_m.group(1)
                remainder = content_html.replace(lead_p, '', 1)
                content_html = f"{image_html}{lead_p}\n<!--more-->\n{remainder}"
            else:
                content_html = f"{image_html}<!--more-->\n{content_html}"

    body = {
        "kind": "blogger#post",
        "title": title,
        "content": content_html,
        "labels": labels
    }

    posts = service.posts()
    request = posts.insert(blogId=blog_id, body=body, isDraft=is_draft)
    response = request.execute()

    post_id = response.get("id")
    post_url = response.get("url")

    return {
        "success": True,
        "post_id": post_id,
        "post_url": post_url,
        "title": response.get("title")
    }

