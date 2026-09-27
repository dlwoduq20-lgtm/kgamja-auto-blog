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

# Load local .env if present
env_path = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(env_path):
    try:
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ[k.strip()] = v.strip()
    except Exception:
        pass

# Gemini API Key
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
