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

CHUNK_SIZE = 4000   # Bark body character limit per message

def _split(text: str, size: int) -> list[str]:
    """Split text into chunks of at most *size* chars, breaking on newlines where possible."""
    chunks = []
    while len(text) > size:
        cut = text.rfind("\n", 0, size)
        if cut == -1:
            cut = size
        chunks.append(text[:cut])
        text = text[cut:].lstrip("\n")
    if text:
        chunks.append(text)
    return chunks

def send_report(subject: str, body: str, recipient: str = ""):
    if BARK_KEY == "YOUR_BARK_KEY_HERE":
        print("[bark] BARK_KEY not set — skipping notification.")
        return

    chunks = _split(body, CHUNK_SIZE)
    ascii_subject = subject.encode("ascii", errors="replace").decode("ascii")

    try:
        for i, chunk in enumerate(chunks, 1):
            title = ascii_subject if len(chunks) == 1 else f"{ascii_subject} ({i}/{len(chunks)})"
            r = requests.post(
                BARK_URL,
                json={
                    "device_key": BARK_KEY,
                    "title": title,
                    "body": chunk,
                    "isArchive": "1",
                },
                timeout=15,
            )
            r.raise_for_status()
        print(f"[bark] Sent {len(chunks)} message(s).")
    except Exception as e:
        print(f"[bark] Send failed: {e}")
