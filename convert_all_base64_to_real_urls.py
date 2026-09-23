"""
Batch Convert all Base64 images in LIVE posts across all 4 blogs to real CDN URLs.
This allows Google Blogger's thumbnail parser to immediately extract and display
thumbnails on the homepage for every post without manual editor saving.
"""

import sys
import json
import base64
import re
import time
import requests

sys.stdout.reconfigure(encoding='utf-8')

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

with open('blogger_credentials.json', 'r', encoding='utf-8') as f:
    c = json.load(f)

creds = Credentials(
    token=c.get('token'),
    refresh_token=c.get('refresh_token'),
    token_uri='https://oauth2.googleapis.com/token',
    client_id=c.get('client_id'),
    client_secret=c.get('client_secret'),
    scopes=['https://www.googleapis.com/auth/blogger']
)

service = build('blogger', 'v3', credentials=creds)

BLOGS = [
    ('StackPilot (US SaaS)', '1939932974175805877'),
    ('GreenThumb (US Garden)', '7758791627533733698'),
    ('생활 속 법과 금융 (KR)', '3888865366756619756'),
    ('暮らしの法律とお金の知恵 (JP)', '4884263507030240234')
]

CATBOX_URL = 'https://catbox.moe/user/api.php'

def upload_bytes_to_catbox(img_bytes: bytes, filename: str = 'thumbnail.jpg') -> str:
    try:
        res = requests.post(
            CATBOX_URL,
            data={'reqtype': 'fileupload'},
            files={'fileToUpload': (filename, img_bytes, 'image/jpeg')},
            timeout=20
        )
        if res.status_code == 200 and res.text.strip().startswith('http'):
            return res.text.strip()
    except Exception as e:
        print(f'    ⚠️ Catbox upload error: {e}')
    return None

def main():
    print('=' * 70)
    print('STARTING BATCH BASE64 TO REAL CDN URL CONVERSION FOR ALL 4 BLOGS')
    print('=' * 70)

    total_converted = 0
    total_checked = 0

    for bname, bid in BLOGS:
        print(f'\n>>> Scanning Blog: {bname} ({bid}) <<<')
        posts = service.posts().list(blogId=bid, status=['LIVE'], maxResults=25).execute().get('items', [])
        print(f'  Found {len(posts)} LIVE posts.')

        blog_converted = 0

        for idx, p in enumerate(posts):
            total_checked += 1
            pid = p['id']
            title = p.get('title', 'Untitled')
            content = p.get('content', '')

            # Check if post has base64 image
            b64_matches = re.findall(r'src=[\"\']data:image/[^;]+;base64,([^\"\']+)[\"\']', content)

            if b64_matches:
                print(f'  [{idx+1}/{len(posts)}] Converting Base64 image in: {title[:40]}...')
                new_content = content
                for b64_str in b64_matches:
                    try:
                        img_bytes = base64.b64decode(b64_str)
                        real_url = upload_bytes_to_catbox(img_bytes)
                        if real_url:
                            # Replace data:image... with real_url
                            pattern = f'data:image/[^;]+;base64,{re.escape(b64_str)}'
                            new_content = re.sub(pattern, real_url, new_content)
                            print(f'    -> Uploaded to CDN: {real_url}')
                        else:
                            print('    -> Failed to get CDN URL!')
                    except Exception as e:
                        print(f'    -> Error decoding/uploading: {e}')

                # Update post if changes made
                if new_content != content:
                    try:
                        service.posts().patch(blogId=bid, postId=pid, body={'content': new_content}).execute()
                        blog_converted += 1
                        total_converted += 1
                        print(f'    [OK] Post {pid} updated successfully!')
                        time.sleep(0.3)
                    except Exception as e:
                        print(f'    [ERROR] Failed to patch post {pid}: {e}')
            else:
                # Already has real URL or no base64
                print(f'  [{idx+1}/{len(posts)}] Clean (Already has real URL): {title[:40]}')

        print(f'  Done {bname}: {blog_converted} posts converted to real URLs.')

    print('\n' + '=' * 70)
    print(f'ALL DONE! Total checked: {total_checked}, Total converted: {total_converted}')
    print('=' * 70)

if __name__ == '__main__':
    main()
