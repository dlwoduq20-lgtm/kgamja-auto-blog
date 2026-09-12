"""
24/7 Smart Dual Scheduler Runner for GitHub Actions
Automatically detects scheduled hours (09:00, 12:00, 17:00, 20:00 KST/JST)
and publishes both Korean and Japanese blog posts seamlessly.
"""
import os
import sys
import json
import subprocess
from datetime import datetime, timezone, timedelta

# Force UTF-8 encoding on Windows consoles
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

# KST and JST are both UTC+9
KST = timezone(timedelta(hours=9))
TARGET_HOURS = [9, 12, 17, 20]
HISTORY_FILE = "published_history.json"


def load_history():
    if not os.path.exists(HISTORY_FILE):
        return {}
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_history(history):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


def run_all_publish():
    """
    Run Korean, Japanese, US B2B SaaS, and Home & Garden auto-posting pipelines.
    """
    print("\n🇰🇷 [한국어 블로그 발행 시작]")
    res_kr = subprocess.run([sys.executable, "main.py", "--next"])
    
    print("\n🇯🇵 [일본어 블로그 발행 시작]")
    res_jp = subprocess.run([sys.executable, "main_jp.py", "--next"])

    print("\n🇺🇸 [미국 B2B SaaS 블로그 발행 시작]")
    res_us = subprocess.run([sys.executable, "main_us.py", "--next"])

    print("\n🌱 [Home & Garden 원예/농업 블로그 발행 시작]")
    res_garden = subprocess.run([sys.executable, "main_garden.py", "--next"])

    return res_kr.returncode == 0 or res_jp.returncode == 0 or res_us.returncode == 0 or res_garden.returncode == 0


def main():
    force_run = os.environ.get("GITHUB_EVENT_NAME") == "workflow_dispatch" or "--force" in sys.argv

    utc_now = datetime.now(timezone.utc)
    kst_now = utc_now.astimezone(KST)
    today_str = kst_now.strftime("%Y-%m-%d")
    current_hour = kst_now.hour
    current_minute = kst_now.minute

    print(f"🕒 [스마트 4대 글로벌 블로그 스케줄러] 현재 시각(KST/JST): {kst_now.strftime('%Y-%m-%d %H:%M:%S')}")
    
    history = load_history()
    today_history = history.get(today_str, [])

    if force_run:
        print("⚡ [수동 실행 감지] 한국·일본·미국SaaS·원예 4대 블로그 동시 발행을 시작합니다.")
        success = run_all_publish()
        if success:
            today_history.append(f"manual_{kst_now.strftime('%H%M')}")
            history[today_str] = today_history
            save_history(history)
            sys.exit(0)
        else:
            sys.exit(1)

    if current_hour in TARGET_HOURS:
        hour_key = f"hour_{current_hour}"
        if hour_key not in today_history:
            print(f"🎯 [발행 시점 도달] 오늘 {current_hour}시 글 발행을 시작합니다 (4대 블로그 동시)!")
            success = run_all_publish()
            if success:
                today_history.append(hour_key)
                history[today_str] = today_history
                save_history(history)
                print(f"✅ {current_hour}시 한국·일본·미국SaaS·원예 4대 블로그 동시 발행 완료 및 기록 저장 성공!")
                sys.exit(0)
            else:
                print(f"❌ 글 발행 중 오류 발생")
                sys.exit(1)
        else:
            print(f"ℹ️ 오늘 {current_hour}시 글은 이미 정상 발행되었습니다 (중복 방지).")
            sys.exit(0)
    else:
        print(f"⏳ 현재 시각({current_hour}시 {current_minute}분)은 발행 목표 시간(9시, 12시, 17시, 20시)이 아닙니다. 대기합니다.")
        sys.exit(0)


if __name__ == "__main__":
    main()
