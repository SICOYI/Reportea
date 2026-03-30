"""
email_sender.py

Sends the daily digest via QQ Mail SMTP (SSL, port 465).

Setup (one-time):
  1. 登录 QQ 邮箱网页版 → 设置 → 账户 → POP3/IMAP/SMTP 服务
  2. 开启「SMTP 服务」，按提示发送短信验证，获得「授权码」
  3. 将授权码填入下方 AUTH_CODE（不是 QQ 密码）

Dependencies: Python standard library only (smtplib, ssl).
"""

import smtplib
import ssl
from email.mime.text import MIMEText

# ── Config ────────────────────────────────────────────────────────────────────

SENDER    = "YOUR_QQ@qq.com"        # 你的 QQ 邮箱地址
AUTH_CODE = "YOUR_AUTH_CODE_HERE"   # QQ 邮箱授权码，非 QQ 密码
RECIPIENT = "wy15123251601@163.com" # 收件地址

SMTP_HOST = "smtp.qq.com"
SMTP_PORT = 465

# ── Send ──────────────────────────────────────────────────────────────────────

def send_report(subject: str, body: str, recipient: str = RECIPIENT):
    """Send *body* (plain text / Markdown) to *recipient* via 163 SMTP."""
    if AUTH_CODE == "YOUR_AUTH_CODE_HERE":
        print("[email] AUTH_CODE not set — skipping email send.")
        return

    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"]    = SENDER
    msg["To"]      = recipient

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, context=context) as server:
            server.login(SENDER, AUTH_CODE)
            server.sendmail(SENDER, [recipient], msg.as_string())
        print(f"[email] Report sent to {recipient}")
    except Exception as e:
        print(f"[email] Send failed: {e}")
