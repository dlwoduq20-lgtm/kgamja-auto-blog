@echo off
chcp 65001 > nul
set PYTHONIOENCODING=utf-8
cd /d "C:\Users\dlwod\.gemini\antigravity\scratch\kgamja_auto_blog"
echo [%date% %time%] 워드프레스 자동 포스팅 시작... >> scheduler_log.txt
"C:\Users\dlwod\AppData\Local\Programs\Python\Python310\python.exe" main.py --next --status publish >> scheduler_log.txt 2>&1
echo [%date% %time%] 포스팅 완료. >> scheduler_log.txt
