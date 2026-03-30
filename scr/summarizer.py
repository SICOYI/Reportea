"""
summarizer.py

Reads all *.md summaries in summaries/ (excluding *report.md),
asks Claude to generate a ≤500-word digest, and saves it as
summaries/{YYYY-MM-DD}report.md
"""

import subprocess
from datetime import datetime
from pathlib import Path

try:
    from email_sender import send_report
    _EMAIL_AVAILABLE = True
except ImportError:
    _EMAIL_AVAILABLE = False

CLAUDE_BIN = "/Users/mac/.vscode/extensions/anthropic.claude-code-2.1.87-darwin-x64/resources/native-binary/claude"

ROOT       = Path(__file__).parent.parent
OUTPUT_DIR = ROOT / "summaries"

def call_claude(prompt: str) -> str:
    result = subprocess.run(
        [CLAUDE_BIN, "-p", prompt],
        capture_output=True, text=True
    )
    return result.stdout.strip()

def generate_daily_report() -> Path | None:
    md_files = sorted(
        p for p in OUTPUT_DIR.glob("*.md")
        if not p.name.endswith("report.md")
    )
    if not md_files:
        print("[summarizer] No summaries found — skipping report.")
        return None

    print(f"\n[summarizer] Generating daily report from {len(md_files)} summary file(s) ...")

    combined = ""
    for md in md_files:
        combined += f"\n\n---\n### {md.stem}\n"
        combined += md.read_text(encoding="utf-8")[:2000]   # cap each paper's contribution

    today_display = datetime.now().strftime("%B %d, %Y")
    prompt = (
        f"You are the editor of a daily science & technology newspaper. "
        f"Today is {today_display}. "
        "Below are structured summaries of several academic papers published or reviewed today. "
        "Write a daily tech report in Markdown, styled like a newspaper front page, "
        "STRICTLY under 1500 words total. Use this exact structure:\n\n"
        "---\n"
        "# 📰 Tech & Research Daily\n"
        f"### {today_display}\n"
        "---\n\n"
        "## 🔬 Today's Research Highlights\n"
        "[2–3 sentence lead that captures the overarching theme of today's papers, "
        "written in an engaging journalistic tone]\n\n"
        "## 📌 Key Stories\n"
        "[For each major finding or contribution, write a short news-style paragraph "
        "with a bold headline, like a newspaper article stub. 3–5 items max.]\n\n"
        "## 💡 What This Means\n"
        "[2–3 sentences on real-world impact or why these findings matter to the broader field]\n\n"
        "## 🔭 On the Horizon\n"
        "[1–2 sentences on open questions or what researchers should watch next]\n\n"
        "---\n"
        "Do NOT list papers by title. Synthesize across them like a journalist, not a librarian.\n\n"
        f"Paper summaries:\n{combined}"
    )

    report = call_claude(prompt)

    today = datetime.now().strftime("%Y-%m-%d")
    out_path = OUTPUT_DIR / f"{today}report.md"
    out_path.write_text(report, encoding="utf-8")
    print(f"    Report saved to: {out_path}")

    if _EMAIL_AVAILABLE:
        subject = f"Tech & Research Daily — {today_display}"
        send_report(subject, report)

    return out_path

if __name__ == "__main__":
    out = generate_daily_report()
    if out:
        print(f"\nDone → {out}")
