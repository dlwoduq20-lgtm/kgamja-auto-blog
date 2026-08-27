@echo off
set PYTHONIOENCODING=utf-8
cd /d "C:\Users\dlwod\.gemini\antigravity\scratch\kgamja_auto_blog"
"C:\Users\dlwod\AppData\Local\Programs\Python\Python310\python.exe" main.py --next --status publish >> scheduler_log.txt 2>&1
