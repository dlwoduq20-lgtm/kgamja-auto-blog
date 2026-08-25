"""
Configuration for kgamjablog.blog automation
"""
import os

# WordPress Site Info
WP_URL = os.environ.get("WP_URL", "https://kgamjablog.blog")
WP_USER = os.environ.get("WP_USER", "dlwoduq20@gmail.com")
WP_APP_PASSWORD = os.environ.get("WP_APP_PASSWORD", "I1iA ftrX wWya cjzX 5b1Q Ck4A")

# Gemini API Key
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "AIzaSyDBAg61kt8TQM_FRUTnxgFKYeUaujyyRSo")

# OpenAI API Key (Optional fallback)
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")

# Category Mappings from kgamjablog.blog
CATEGORY_MAP = {
    "대출 기초": 764247278,
    "대출 후기": 764247281,
    "신용대출": 764247279,
    "정부지원 대출": 764247280,
    "채무분쟁": 764247290,
    "민사소송": 764247294,
    "형사문제": 764247289,
    "이혼가사": 764247288,
    "생활법률": 764247287,
    "생활분쟁": 764247293,
    "부동산분쟁": 764247291,
    "계약사기": 764247292,
    "금융 뉴스": 764247282,
    "가상화폐 정보": 764247295
}
