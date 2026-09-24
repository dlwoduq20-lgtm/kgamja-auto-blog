"""
Configuration for kgamja_auto_blog (Google Blogger Edition)
"""
import os

# Blog Target Settings
BLOG_PLATFORM = "blogger"
BLOGGER_EMAIL = os.environ.get("BLOGGER_EMAIL", "dlwoduq20.post2026@blogger.com")
BLOG_URL = "https://kgamjablog.blogspot.com"

# SMTP Settings for Automated Publishing
SMTP_USER = os.environ.get("SMTP_USER", "")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "")
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# Gemini API Key
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
