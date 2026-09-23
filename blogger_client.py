"""
Google Blogger API v3 Client for kgamjablog & seikatsulaw
"""
import os
import json
import base64
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

BLOG_ID_KR = "3888865366756619756"
BLOG_ID_JP = "4884263507030240234"
SCOPES = ["https://www.googleapis.com/auth/blogger"]


import requests
import re


def upload_image_to_cdn(image_bytes: bytes) -> str:
    """
    Upload image bytes to CDN to obtain a permanent https:// image URL.
    This enables Blogger's thumbnail engine to immediately extract and display
    thumbnails on the homepage without requiring manual editor re-saves.
    """
    if not image_bytes:
        return None
    try:
        url = "https://catbox.moe/user/api.php"
        res = requests.post(
            url,
            data={"reqtype": "fileupload"},
            files={"fileToUpload": ("illustration.jpg", image_bytes, "image/jpeg")},
            timeout=15
        )
        if res.status_code == 200 and res.text.startswith("http"):
            return res.text.strip()
    except Exception as e:
        print(f"⚠️ Image CDN upload failed, falling back to base64: {e}")
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
            f'<div style="text-align: center; margin: 0 0 25px 0;">\n'
            f'  <img src="{img_src}" alt="{title}" '
            f'style="max-width: 100%; height: auto; border-radius: 12px; box-shadow: 0 4px 16px rgba(0,0,0,0.12); display: inline-block;" />\n'
            f'</div>\n\n'
        )
        if "<!--more-->" in content_html:
            content_html = image_html + content_html
        else:
            p_m = re.search(r'(<p[^>]*>.*?</p>)', content_html, re.S)
            if p_m:
                lead_p = p_m.group(1)
                remainder = content_html.replace(lead_p, '', 1)
                content_html = f"{lead_p}\n<!--more-->\n{image_html}{remainder}"
            else:
                content_html = image_html + content_html

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

