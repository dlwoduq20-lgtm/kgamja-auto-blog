"""
Configuration for kgamja_auto_blog
"""
import os

# WordPress Settings
# Use environment variables if set (e.g. in GitHub Actions), otherwise use defaults
WP_URL = os.environ.get("WP_URL", "https://kgamjablog.wpcomstaging.com")
WP_USER = os.environ.get("WP_USER", "dlwoduq20@gmail.com")
WP_APP_PASSWORD = os.environ.get("WP_APP_PASSWORD", "I1iA ftrX wWya cjzX 5b1Q Ck4A")

# Gemini API Key
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "AIzaSyDBAg61kt8TQM_FRUTnxgFKYeUaujyyRSo")

# Blog Category Name -> WordPress Category ID Map
CATEGORY_MAP = {
    "대출 기초": 4,
    "대출 후기": 16,
    "신용대출": 17,
    "정부지원 대출": 18,
    "채무분쟁": 20,
    "민사소송": 21,
    "형사문제": 22,
    "이혼가사": 23,
    "생활법률": 24,
    "생활분쟁": 25,
    "부동산분쟁": 26,
    "계약사기": 27,
    "금융 뉴스": 28
}
