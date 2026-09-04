"""
Smart Cloud Scheduler Runner for GitHub Actions
Runs every 20 minutes in GitHub Cloud, ensuring 100% reliable 4-times-daily posting.
Never sleeps or misses posts even when PC is completely turned off.
"""
import sys
import os
import json
import datetime
import subprocess

# Reconfigure stdout for Windows & Linux console UTF-8 support
sys.stdout.reconfigure(encoding='utf-8')

HISTORY_FILE = "published_history.json"
TARGET_HOURS = [9, 12, 17, 20]  # KST target hours


def get_kst_now():
    utc_now = datetime.datetime.now(datetime.timezone.utc)
    kst_tz = datetime.timezone(datetime.timedelta(hours=9))
    return utc_now.astimezone(kst_tz)


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


def main():
    force_run = "--force" in sys.argv or os.environ.get("GITHUB_EVENT_NAME") == "workflow_dispatch"
    
    kst_now = get_kst_now()
    today_str = kst_now.strftime("%Y-%m-%d")
    current_hour = kst_now.hour
    current_minute = kst_now.minute

    print(f"🕒 [스마트 클라우드 스케줄러] 현재 한국 시각(KST): {kst_now.strftime('%Y-%m-%d %H:%M:%S')}")
    
    history = load_history()
    today_history = history.get(today_str, [])

    # If manual run or force run
    if force_run:
        print("⚡ [수동 실행 감지] 시간 제한 없이 즉시 글 생성을 시작합니다.")
        res = subprocess.run([sys.executable, "main.py", "--next"])
        if res.returncode == 0:
            today_history.append(f"manual_{kst_now.strftime('%H%M')}")
            history[today_str] = today_history
            save_history(history)
            sys.exit(0)
        else:
            sys.exit(res.returncode)

    # Check if current hour is one of the target hours (9, 12, 17, 20)
    if current_hour in TARGET_HOURS:
        hour_key = f"hour_{current_hour}"
        if hour_key not in today_history:
            print(f"🎯 [발행 시점 도달] 오늘 {current_hour}시 글이 아직 발행되지 않았습니다. 즉시 발행을 시작합니다!")
            res = subprocess.run([sys.executable, "main.py", "--next"])
            if res.returncode == 0:
                today_history.append(hour_key)
                history[today_str] = today_history
                save_history(history)
                print(f"✅ {current_hour}시 글 발행 완료 및 기록 저장 성공!")
                sys.exit(0)
            else:
                print(f"❌ 글 발행 중 오류 발생 (코드: {res.returncode})")
                sys.exit(res.returncode)
        else:
            print(f"ℹ️ 오늘 {current_hour}시 글은 이미 정상 발행되었습니다 (중복 방지).")
            sys.exit(0)
    else:
        print(f"⏳ 현재 시각({current_hour}시 {current_minute}분)은 발행 목표 시간(9시, 12시, 17시, 20시)이 아닙니다. 대기합니다.")
        sys.exit(0)


if __name__ == "__main__":
    main()
