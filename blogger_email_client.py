"""
Blogger Email Client for kgamjablog.blogspot.com
Sends high-quality AI generated SEO posts with FLUX photorealistic images to Blogger secret email.
"""
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

BLOGGER_EMAIL = "dlwoduq20.post2026@blogger.com"


def send_post_via_email(
    title: str,
    content_html: str,
    tags: list,
    smtp_user: str = None,
    smtp_password: str = None,
    smtp_server: str = "smtp.gmail.com",
    smtp_port: int = 587
) -> dict:
    """
    Send blog post to Blogger secret email using SMTP.
    """
    smtp_user = smtp_user or os.environ.get("SMTP_USER", "dlwoduq20@gmail.com")
    smtp_password = smtp_password or os.environ.get("SMTP_PASSWORD")

    if not smtp_password:
        raise ValueError("SMTP_PASSWORD is not configured.")

    # In Blogger email publishing, tags can be placed in the body or subject with '#'
    tags_formatted = " ".join([f"#{t.replace(' ', '')}" for t in tags]) if tags else ""
    full_html_content = f"{content_html}\n<p style='margin-top: 30px; color: #888;'>태그: {tags_formatted}</p>"

    msg = MIMEMultipart("alternative")
    msg["From"] = smtp_user
    msg["To"] = BLOGGER_EMAIL
    msg["Subject"] = title

    part_html = MIMEText(full_html_content, "html", "utf-8")
    msg.attach(part_html)

    try:
        if smtp_port == 465:
            server = smtplib.SMTP_SSL(smtp_server, smtp_port, timeout=20)
        else:
            server = smtplib.SMTP(smtp_server, smtp_port, timeout=20)
            server.starttls()

        server.login(smtp_user, smtp_password)
        server.sendmail(smtp_user, [BLOGGER_EMAIL], msg.as_string())
        server.quit()

        print(f"📧 이메일 발송 성공 -> {BLOGGER_EMAIL} (제목: {title})")
        return {"success": True, "title": title, "recipient": BLOGGER_EMAIL}
    except Exception as e:
        print(f"⚠️ 이메일 발송 실패: {e}")
        return {"success": False, "error": str(e)}
