import sys
import os
import json
import subprocess
from google_auth_oauthlib.flow import InstalledAppFlow

sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
sys.stderr.reconfigure(encoding='utf-8', line_buffering=True)

SCOPES = ["https://www.googleapis.com/auth/blogger"]


class UrlHook(str):
    def format(self, *args, **kwargs):
        url = kwargs.get("url", "")
        with open("oauth_url.txt", "w", encoding="utf-8") as f:
            f.write(url)
        try:
            subprocess.Popen(f'cmd.exe /c start "" "{url}"', shell=True)
        except Exception:
            pass
        return f"\n============================================================\n[구글 로그인 및 연동 링크]\n브라우저 창이 자동으로 열리지 않는 경우 아래 링크를 열어주세요:\n{url}\n============================================================\n"


def run_oauth_flow(client_id: str, client_secret: str):
    client_config = {
        "installed": {
            "client_id": client_id,
            "client_secret": client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": ["http://localhost:8080/"]
        }
    }
    flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
    
    print("🚀 구글 로그인 및 블로그 권한 허용 창을 준비 중입니다...", flush=True)
    creds = flow.run_local_server(
        port=8080,
        authorization_prompt_message=UrlHook("Open: {url}"),
        prompt="consent",
        access_type="offline"
    )

    cred_data = {
        "client_id": client_id,
        "client_secret": client_secret,
        "token": creds.token,
        "refresh_token": creds.refresh_token
    }

    with open("blogger_credentials.json", "w", encoding="utf-8") as f:
        json.dump(cred_data, f, indent=2)

    print("\n" + "=" * 60, flush=True)
    print("🎉 [구글 블로거 공식 API 연동 성공!]", flush=True)
    print("blogger_credentials.json에 영구 리프레시 토큰이 안전하게 저장되었습니다.", flush=True)
    print("이제 이메일 차단 없이 100% 안정적으로 글이 등록됩니다!", flush=True)
    print("=" * 60, flush=True)
    return cred_data


if __name__ == "__main__":
    cid = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("GOOGLE_CLIENT_ID", "")
    sec = sys.argv[2] if len(sys.argv) > 2 else os.environ.get("GOOGLE_CLIENT_SECRET", "")
    if not cid or not sec:
        print("Usage: python setup_blogger_oauth.py <client_id> <client_secret>")
        sys.exit(1)
    run_oauth_flow(cid, sec)

