"""
email_sender.py

Sends the daily digest to your iPhone via Bark push notifications.

Setup (one-time):
  1. App Store 安装 Bark
  2. 打开 app，首页显示你的专属 URL，格式：https://api.day.re/xxxxxxxxxx
  3. 将末尾的 key 填入下方 BARK_KEY

Dependencies: requests  (pip install requests)
"""

import requests

# ── Config ────────────────────────────────────────────────────────────────────

BARK_KEY = "5kgkavK6PevWSZVQoNqFSQ"

BARK_URL = "https://api.day.app/push"

# ── Send ──────────────────────────────────────────────────────────────────────

def send_report(subject: str, body: str, recipient: str = ""):
    if BARK_KEY == "YOUR_BARK_KEY_HERE":
        print("[bark] BARK_KEY not set — skipping notification.")
        return

    # Bark body limit is ~4000 chars; truncate with notice if needed
    if len(body) > 4000:
        body = body[:3970] + "\n\n...[truncated]"

    try:
        r = requests.post(
            BARK_URL,
            json={
                "device_key": BARK_KEY,
                "title": subject.encode("ascii", errors="replace").decode("ascii"),
                "body": body,
                "isArchive": "1",    # save in Bark history so you can re-read anytime
            },
            timeout=15,
        )
        r.raise_for_status()
        print(f"[bark] Notification sent.")
    except Exception as e:
        print(f"[bark] Send failed: {e}")
