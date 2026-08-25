"""
Standalone Python Scheduler for kgamjablog.blog
Runs daily at 09:00, 12:00, 17:00, 20:00.
"""
import sys
import time
import datetime
import subprocess

# Reconfigure stdout for Windows console UTF-8 support
sys.stdout.reconfigure(encoding='utf-8')

# Target posting times (24-hour format)
DAILY_POST_TIMES = ["09:00", "12:00", "17:00", "20:00"]


def run_post_task():
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n[{now_str}] ⏰ 스케줄러 트리거: 워드프레스 자동 포스팅을 실행합니다...")
    try:
        res = subprocess.run(
            [sys.executable, "main.py", "--next", "--status", "publish"],
            capture_output=True,
            text=True,
            encoding="utf-8"
        )
        print(res.stdout)
        if res.stderr:
            print("Stderr:", res.stderr)
    except Exception as e:
        print(f"⚠️ 스케줄러 실행 오류: {e}")


def main():
    print("=" * 60)
    print("🤖 kgamjablog.blog 자동 포스팅 스케줄러가 시작되었습니다.")
    print(f"📅 매일 자동 발행 예정 시각: {', '.join(DAILY_POST_TIMES)}")
    print("💡 이 창을 켜두시면 해당 시간마다 자동으로 큐의 글이 블로그에 발행됩니다.")
    print("=" * 60)

    last_run_date = ""

    while True:
        now = datetime.datetime.now()
        current_time_str = now.strftime("%H:%M")
        current_date_str = now.strftime("%Y-%m-%d")

        for target_time in DAILY_POST_TIMES:
            run_key = f"{current_date_str}_{target_time}"
            if current_time_str == target_time and last_run_date != run_key:
                last_run_date = run_key
                run_post_task()

        # Check every 30 seconds
        time.sleep(30)


if __name__ == "__main__":
    main()
