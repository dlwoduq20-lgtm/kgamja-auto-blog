"""
Apply snippet <!--more--> tag to all 18 LIVE posts across all 4 blogs
so that 6-7 rich post cards render on the homepage instead of just 1.
"""

import json
import re
import sys
import time

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

blogs = [
    ('暮らしの法律とお金の知恵 (JP)', '4884263507030240234')
]

for bname, bid in blogs:
    print('=' * 65)
    print(f'Processing {bname}...')
    posts = service.posts().list(blogId=bid, status=['LIVE'], maxResults=25).execute().get('items', [])
    print(f'  Found {len(posts)} LIVE posts.')

    for idx, p in enumerate(posts):
        pid = p['id']
        title = p.get('title', '')
        content = p.get('content', '')

        # Remove existing <!--more-->
        clean_content = content.replace('<!--more-->', '')

        # Look for heavy base64 image or first illustration block
        img_match = re.search(r'(<div[^>]*text-align:\s*center[^>]*>.*?<img[^>]*data:image.*?</div>)', clean_content, re.S)
        if img_match:
            img_block = img_match.group(1)
            rest_content = clean_content.replace(img_block, '')
            first_p_m = re.search(r'(<p[^>]*>.*?</p>)', rest_content, re.S)
            if first_p_m:
                lead_p = first_p_m.group(1)
                body_remainder = rest_content.replace(lead_p, '', 1)
                new_content = f"{lead_p}\n<!--more-->\n{img_block}\n{body_remainder}"
            else:
                new_content = f"<p style='font-size: 16px;'>{title}</p>\n<!--more-->\n{clean_content}"
        else:
            first_p_m = re.search(r'(<p[^>]*>.*?</p>)', clean_content, re.S)
            if first_p_m:
                lead_p = first_p_m.group(1)
                body_remainder = clean_content.replace(lead_p, '', 1)
                new_content = f"{lead_p}\n<!--more-->\n{body_remainder}"
            else:
                new_content = clean_content[:300] + '\n<!--more-->\n' + clean_content[300:]

        try:
            service.posts().patch(blogId=bid, postId=pid, body={'content': new_content}).execute()
            print(f'  [{idx+1}/{len(posts)}] Patched snippet for: {title[:40]}...')
            time.sleep(0.15)
        except Exception as e:
            print(f'  [ERROR] {pid}: {e}')

print('\nALL BLOGS POST SNIPPET OPTIMIZATION COMPLETED!')
