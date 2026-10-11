"""
Publish One Post Each to All 4 Global Blogs
Executes:
1. KR (kgamjablog.blogspot.com)
2. JP (seikatsulaw.blogspot.com)
3. US B2B SaaS (stackpilot.blogspot.com)
4. Home & Garden (greenthumb-garden.blogspot.com)
"""
import sys
import subprocess

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

BLOGS = [
    {"name": "🇰🇷 한국어 블로그 (생활법률/재테크)", "cmd": [sys.executable, "main.py", "--next"]},
    {"name": "🇯🇵 일본어 블로그 (暮らしの法律とお金の知恵)", "cmd": [sys.executable, "main_jp.py", "--next"]},
    {"name": "🇺🇸 미국 B2B SaaS 블로그 (StackPilot Reviews)", "cmd": [sys.executable, "main_us.py", "--next"]},
    {"name": "🌱 Home & Garden 블로그 (GreenThumb Garden)", "cmd": [sys.executable, "main_garden.py", "--next"]},
]

def main():
    print("=" * 70)
    print("🚀 [4개 블로그 각 1개 글 수동 발행 작업 시작]")
    print("=" * 70)

    results = {}
    for blog in BLOGS:
        print(f"\n▶️ [{blog['name']}] 발행 프로세스 실행 중...")
        res = subprocess.run(blog["cmd"])
        status = "성공" if res.returncode == 0 else "실패"
        results[blog["name"]] = status
        print(f"🏁 [{blog['name']}] 실행 완료: {status} (코드: {res.returncode})")

    print("\n" + "=" * 70)
    print("📊 [4개 블로그 최종 발행 결과 요약]")
    print("=" * 70)
    for name, status in results.items():
        icon = "✅" if status == "성공" else "❌"
        print(f"{icon} {name}: {status}")
    print("=" * 70)

if __name__ == "__main__":
    main()
