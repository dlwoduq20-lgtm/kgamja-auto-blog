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



def update_github_secret(secret_name: str, secret_value: str) -> bool:
    try:
        import base64
        from nacl import encoding, public
        import requests

        gh_token = "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"
        repo = "dlwoduq20-lgtm/kgamja-auto-blog"
        headers = {
            "Authorization": f"Bearer {gh_token}",
            "Accept": "application/vnd.github+json"
        }
        r = requests.get(f"https://api.github.com/repos/{repo}/actions/secrets/public-key", headers=headers)
        if r.status_code != 200:
            print(f"⚠️ GitHub Secret 공개키 획득 실패: {r.text}")
            return False
        key_data = r.json()
        public_key_b64 = key_data["key"]
        key_id = key_data["key_id"]

        pub_key = public.PublicKey(public_key_b64.encode("utf-8"), encoding.Base64Encoder())
        sealed_box = public.SealedBox(pub_key)
        encrypted = sealed_box.encrypt(secret_value.encode("utf-8"))
        encrypted_value = base64.b64encode(encrypted).decode("utf-8")

        put_data = {
            "encrypted_value": encrypted_value,
            "key_id": key_id
        }
        r_put = requests.put(f"https://api.github.com/repos/{repo}/actions/secrets/{secret_name}", headers=headers, json=put_data)
        if r_put.status_code in [201, 204]:
            print(f"✅ GitHub Actions Secret '{secret_name}' 자동 동기화 성공!")
            return True
        else:
            print(f"⚠️ GitHub Actions Secret 업데이트 응답 ({r_put.status_code}): {r_put.text}")
            return False
    except Exception as e:
        print(f"⚠️ GitHub Actions Secret 동기화 중 오류: {e}")
        return False


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
    print("blogger_credentials.json에 새 리프레시 토큰이 안전하게 저장되었습니다.", flush=True)
    
    # Automatically sync to GitHub Actions secrets
    update_github_secret("BLOGGER_CREDENTIALS", json.dumps(cred_data))
    
    print("이제 이메일 차단 없이 100% 안정적으로 글이 등록됩니다!", flush=True)
    print("=" * 60, flush=True)
    return cred_data


if __name__ == "__main__":
    cid = sys.argv[1] if len(sys.argv) > 1 else ""
    sec = sys.argv[2] if len(sys.argv) > 2 else ""
    if not cid or not sec:
        if os.path.exists("blogger_credentials.json"):
            try:
                with open("blogger_credentials.json", "r", encoding="utf-8") as f:
                    prev = json.load(f)
                    cid = prev.get("client_id")
                    sec = prev.get("client_secret")
            except Exception:
                pass
    if not cid or not sec:
        cid = os.environ.get("GOOGLE_CLIENT_ID", "679675712497-m0s38cdjno97ha3mlmc2b6n0a6fd4ked.apps.googleusercontent.com")
        sec = os.environ.get("GOOGLE_CLIENT_SECRET", "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")
    run_oauth_flow(cid, sec)

