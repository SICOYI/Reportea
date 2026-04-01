"""
browser.py

Given a paper title, search the web for a freely available PDF and download it.

Search strategy (in order):
  1. Direct HTTP attempt on Google Scholar search URL (no Claude needed)
  2. Claude with WebSearch/WebFetch — searches Google Scholar, arXiv, Semantic Scholar, ResearchGate
  3. Fallback: shorter Claude call limited to arXiv + Semantic Scholar only

Used as the download step in the title-based pipeline (fallback when no DOI is available).
"""

import re
import subprocess
import requests
from pathlib import Path

CLAUDE_BIN = "/Users/mac/.vscode/extensions/anthropic.claude-code-2.1.87-darwin-x64/resources/native-binary/claude"

ROOT      = Path(__file__).parent.parent
CACHE_DIR = ROOT / "pdf_cache"

_HEADERS = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}


def _safe_filename(title: str) -> str:
    """Convert a paper title into a safe filesystem stem (max 80 chars)."""
    clean = re.sub(r'[^\w\s-]', '', title).strip().replace(' ', '_')
    return clean[:80] if clean else "unknown_paper"


def _try_download(url: str, dest: Path) -> bool:
    """Attempt to download a PDF from url to dest. Returns True on success."""
    try:
        r = requests.get(url, headers=_HEADERS, timeout=30, allow_redirects=True)
        if r.status_code == 200 and b"%PDF" in r.content[:10]:
            dest.write_bytes(r.content)
            return True
    except Exception:
        pass
    return False


def _urls_from_claude_response(text: str) -> list[str]:
    """Extract PDF URLs from a Claude response (tagged first, then heuristic)."""
    urls = re.findall(r'PDF_URL:\s*(https?://\S+)', text)
    if not urls:
        all_urls = re.findall(r'https?://[^\s\)\]\"\']+', text)
        urls = [u for u in all_urls if "pdf" in u.lower()]
    return urls


def _run_claude(prompt: str, timeout: int = 300) -> str:
    result = subprocess.run(
        [CLAUDE_BIN, "-p", prompt, "--allowedTools", "WebSearch,WebFetch"],
        capture_output=True, text=True, timeout=timeout,
    )
    return result.stdout


# ── Strategy 1: Claude full search (Google Scholar + arXiv + S2 + ResearchGate) ──

def _search_via_claude_full(title: str) -> list[str]:
    prompt = (
        f'Find a freely available PDF for this academic paper: "{title}". '
        "Search on Google Scholar (https://scholar.google.com), arXiv, "
        "Semantic Scholar, and ResearchGate. "
        "Return every direct PDF URL you find, each on its own line prefixed with 'PDF_URL:'."
    )
    return _urls_from_claude_response(_run_claude(prompt, timeout=300))


# ── Strategy 2: Claude short fallback (arXiv + Semantic Scholar only) ────────

def _search_via_claude_short(title: str) -> list[str]:
    # Keep prompt short to minimise token spend
    short_title = title[:120]
    prompt = (
        f'PDF for: "{short_title}". '
        "Check arXiv and Semantic Scholar. "
        "List PDF URLs prefixed with 'PDF_URL:'."
    )
    return _urls_from_claude_response(_run_claude(prompt, timeout=180))


# ── Main entry point ─────────────────────────────────────────────────────────

def find_and_download_pdf(title: str, output_dir: Path = CACHE_DIR) -> Path | None:
    """
    Search for a freely available PDF of *title* using a three-stage strategy.
    Downloads to *output_dir* and returns the Path, or None if not found.
    """
    output_dir.mkdir(exist_ok=True)
    dest = output_dir / f"{_safe_filename(title)}.pdf"

    if dest.exists():
        print(f"  [browser] Already cached: {dest.name}")
        return dest

    print(f"  [browser] Searching for: {title}")

    # ── Stage 1: Claude full search (Google Scholar priority) ──────────────
    pdf_urls = _search_via_claude_full(title)

    if not pdf_urls:
        print(f"  [browser] Stage 1 found no URLs — trying short fallback prompt")
        # ── Stage 2: Claude short fallback ─────────────────────────────────
        pdf_urls = _search_via_claude_short(title)

    if not pdf_urls:
        print(f"  [browser] No PDF URL found for: {title}")
        return None

    for url in pdf_urls:
        print(f"  [browser] Trying: {url}")
        if _try_download(url, dest):
            print(f"  [browser] Saved: {dest.name}")
            return dest
        print(f"  [browser] Skipped (not a valid PDF)")

    print(f"  [browser] Could not download PDF for: {title}")
    return None
