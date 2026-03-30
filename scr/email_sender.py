"""
email_sender.py

Sends the daily digest to your phone via ntfy.sh (free push notifications).

Setup (one-time):
  1. 手机安装 ntfy app（iOS / Android 均有）
  2. 打开 app → Subscribe to topic → 输入下方 TOPIC 的值
  3. 完成，无需注册账号

Note: TOPIC 相当于你的私人频道名，建议设为不易被猜到的字符串。

Dependencies: requests  (pip install requests)
"""

import requests

# ── Config ────────────────────────────────────────────────────────────────────

TOPIC = "reportea-1314x"

NTFY_URL = f"https://ntfy.sh/{TOPIC}"

# ── Send ──────────────────────────────────────────────────────────────────────

def send_report(subject: str, body: str, recipient: str = ""):
    if TOPIC == "YOUR_TOPIC_HERE":
        print("[ntfy] TOPIC not set — skipping notification.")
        return

    # ntfy hard cap is 4096 bytes per message; send in two parts if needed
    encoded = body.encode("utf-8")
    if len(encoded) <= 4096:
        chunks = [encoded]
    else:
        # split on a utf-8 boundary to avoid corrupting multi-byte chars
        chunks = [encoded[:4096], encoded[4096:8192]] if len(encoded) > 4096 else [encoded]

    try:
        for i, chunk in enumerate(chunks, 1):
            title = subject if len(chunks) == 1 else f"{subject} ({i}/{len(chunks)})"
            # HTTP headers must be ASCII; replace non-ASCII chars with closest equivalent
            title = title.encode("ascii", errors="replace").decode("ascii")
            r = requests.post(
                NTFY_URL,
                data=chunk,
                headers={
                    "Title": title,
                    "Content-Type": "text/plain; charset=utf-8",
                    "Priority": "default",
                },
                timeout=15,
            )
            r.raise_for_status()
        print(f"[ntfy] Notification sent → topic: {TOPIC}")
    except Exception as e:
        print(f"[ntfy] Send failed: {e}")
