"""
Blogger Email Client for kgamjablog.blogspot.com
Attaches photorealistic image files directly with Content-ID (CID)
for 100% reliable Google CDN hosting and zero broken images.
"""
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

BLOGGER_EMAIL = "dlwoduq20.post2026@blogger.com"


def send_post_via_email(
    title: str,
    content_html: str,
    tags: list,
    image_bytes: bytes = None,
    recipient_email: str = None,
    smtp_user: str = None,
    smtp_password: str = None,
    smtp_server: str = "smtp.gmail.com",
    smtp_port: int = 587
) -> dict:
    """
    Send blog post to Blogger secret email using SMTP with CID image attachment.
    """
    target_email = recipient_email or os.environ.get("BLOGGER_EMAIL", BLOGGER_EMAIL)
    smtp_user = smtp_user or os.environ.get("SMTP_USER", "dlwoduq20@gmail.com")
    smtp_password = smtp_password or os.environ.get("SMTP_PASSWORD")

    if not smtp_password:
        raise ValueError("SMTP_PASSWORD is not configured.")

    # 1. Embed CID image block into HTML if image_bytes are present
    if image_bytes:
        image_html = f"""
<div style="text-align: center; margin: 30px auto; max-width: 720px;">
  <img src="cid:post_image" alt="{title}" style="width: 100%; height: auto; border-radius: 10px; box-shadow: 0 4px 16px rgba(0,0,0,0.12);" />
  <p style="color: #777; font-size: 13px; margin-top: 8px; text-align: center;">▲ {title}</p>
</div>
"""
        first_p = content_html.find("</p>")
        if first_p != -1:
            insert_idx = first_p + 4
            content_html = content_html[:insert_idx] + "\n" + image_html + "\n" + content_html[insert_idx:]
        else:
            content_html = image_html + "\n" + content_html

    # 2. Tags formatting for Blogger
    tags_formatted = " ".join([f"#{t.replace(' ', '')}" for t in tags]) if tags else ""
    full_html_content = f"{content_html}\n<p style='margin-top: 30px; color: #888;'>タグ: {tags_formatted}</p>"

    # 3. Create multipart message
    msg = MIMEMultipart("related")
    msg["From"] = smtp_user
    msg["To"] = target_email
    msg["Subject"] = title

    part_html = MIMEText(full_html_content, "html", "utf-8")
    msg.attach(part_html)

    # 4. Attach image with Content-ID <post_image>
    if image_bytes:
        img_part = MIMEImage(image_bytes, name="featured_image.jpg")
        img_part.add_header("Content-ID", "<post_image>")
        img_part.add_header("Content-Disposition", "inline", filename="featured_image.jpg")
        msg.attach(img_part)
        print(f"📎 2D 만화 이미지 CID 파일 첨부 완료 ({len(image_bytes)} bytes)")

    try:
        if smtp_port == 465:
            server = smtplib.SMTP_SSL(smtp_server, smtp_port, timeout=25)
        else:
            server = smtplib.SMTP(smtp_server, smtp_port, timeout=25)
            server.starttls()

        server.login(smtp_user, smtp_password)
        server.sendmail(smtp_user, [target_email], msg.as_string())
        server.quit()

        print(f"📧 이메일 발송 성공 -> {target_email} (제목: {title})")
        return {"success": True, "title": title, "recipient": target_email}
    except Exception as e:
        print(f"⚠️ 이메일 발송 실패: {e}")
        return {"success": False, "error": str(e)}
