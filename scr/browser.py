"""
browser.py

Given a paper title, search the web for a freely available PDF and download it.
Uses the Claude CLI with WebSearch/WebFetch.

Used as the download step in the title-based pipeline (fallback when no DOI is available).
"""

import re
import subprocess
import requests
from pathlib import Path

CLAUDE_BIN = "/Users/mac/.vscode/extensions/anthropic.claude-code-2.1.87-darwin-x64/resources/native-binary/claude"

ROOT      = Path(__file__).parent.parent
CACHE_DIR = ROOT / "pdf_cache"


def _safe_filename(title: str) -> str:
    """Convert a paper title into a safe filesystem stem (max 80 chars)."""
    clean = re.sub(r'[^\w\s-]', '', title).strip().replace(' ', '_')
    return clean[:80] if clean else "unknown_paper"


def find_and_download_pdf(title: str, output_dir: Path = CACHE_DIR) -> Path | None:
    """
    Search the web for a freely available PDF of *title*.
    Download it to *output_dir* if found.
    Returns the Path to the downloaded PDF, or None if not found.
    """
    output_dir.mkdir(exist_ok=True)
    dest = output_dir / f"{_safe_filename(title)}.pdf"

    if dest.exists():
        print(f"  [browser] Already cached: {dest.name}")
        return dest

    print(f"  [browser] Searching for: {title}")

    prompt = (
        f'Find a freely available PDF for this academic paper: "{title}". '
        "Search on arXiv, Semantic Scholar, ResearchGate, and the author's institutional page. "
        "Return every direct PDF URL you find, each on its own line prefixed with 'PDF_URL:'."
    )
    result = subprocess.run(
        [CLAUDE_BIN, "-p", prompt, "--allowedTools", "WebSearch,WebFetch"],
        capture_output=True, text=True, timeout=300
    )

    # Prefer explicitly tagged URLs; fall back to any .pdf URL in the response
    pdf_urls = re.findall(r'PDF_URL:\s*(https?://\S+)', result.stdout)
    if not pdf_urls:
        all_urls = re.findall(r'https?://[^\s\)\]\"\']+', result.stdout)
        pdf_urls = [u for u in all_urls if "pdf" in u.lower()]

    if not pdf_urls:
        print(f"  [browser] No PDF URL found for: {title}")
        return None

    headers = {"User-Agent": "Mozilla/5.0 (research bot)"}
    for url in pdf_urls:
        print(f"  [browser] Trying: {url}")
        try:
            r = requests.get(url, headers=headers, timeout=30, allow_redirects=True)
            if r.status_code == 200 and b"%PDF" in r.content[:10]:
                dest.write_bytes(r.content)
                print(f"  [browser] Saved: {dest.name}")
                return dest
            else:
                print(f"  [browser] Skipped ({r.status_code} or not a PDF)")
        except Exception as e:
            print(f"  [browser] Failed: {e}")

    print(f"  [browser] Could not download PDF for: {title}")
    return None
