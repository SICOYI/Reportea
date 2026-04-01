"""
token_guard.py — Detect Claude API token exhaustion and alert via Bark.
"""

import re
from pathlib import Path

from email_sender import send_report

ROOT       = Path(__file__).parent.parent
OUTPUT_DIR = ROOT / "summaries"

# Patterns Claude returns when the usage limit is hit
_LIMIT_PATTERNS = [
    r"you.ve hit (the|your) (rate |usage |api |message )?limit",
    r"usage limit reached",
    r"out of (api )?credits",
    r"exceeded.*limit",
    r"quota.*exceeded",
    r"claude\.ai/upgrade",   # link Claude sometimes includes in limit messages
]
_LIMIT_RE = re.compile("|".join(_LIMIT_PATTERNS), re.IGNORECASE)


class TokenLimitError(RuntimeError):
    """Raised when Claude signals that the usage limit has been reached."""


def _send_all_summaries() -> None:
    """Push each collected summary file to Bark as a separate message."""
    md_files = sorted(
        p for p in OUTPUT_DIR.glob("*.md")
        if not p.name.endswith("report.md")
    )
    if not md_files:
        send_report("Reportea — No Summaries Yet", "Token limit hit before any summaries were saved.")
        return

    for i, md in enumerate(md_files, 1):
        title = f"Reportea Summary {i}/{len(md_files)}: {md.stem}"
        body = md.read_text(encoding="utf-8")
        send_report(title, body)


def check_for_limit(response: str) -> None:
    """
    Call this after every call_claude() invocation.
    If the response looks like a rate-limit / token-limit message:
      1. Send an alert to Bark.
      2. Push every collected summary to Bark individually.
      3. Raise TokenLimitError so the caller stops gracefully.
    """
    if _LIMIT_RE.search(response):
        send_report(
            "Reportea — Token Limit Hit",
            "Claude token limit reached — pipeline stopped early.\n"
            "All summaries collected so far will follow as separate messages.",
        )
        _send_all_summaries()
        raise TokenLimitError(f"Token limit detected in response: {response[:200]}")
