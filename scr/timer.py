"""
timer.py  —  Main orchestrator for Reportea

Schedule:
  01:00  Wake up

         Initialization
           ├── Build keywords library from base_papers/
           ├── Process base papers (doi-first, title-fallback per paper)
           ├── Clear pdf_cache/
           ├── Generate unified keywords_list.csv (DOIs + titles) from base_papers/ citations
           ├── Compare CSV against library → top-10 related papers
           └── Delete keywords_list.csv

         Loop  (repeats until 03:00)
           ├── Process related papers (doi-first, title-fallback per paper)
           ├── Generate unified keywords_list.csv from pdf_cache/ citations
           ├── Compare CSV against library → next top-10 papers
           ├── Clear pdf_cache/
           └── Delete keywords_list.csv

  03:00  Generate daily digest via summarizer
"""

import argparse
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from extractor import TitleExtractor, extract_pdf_text, DOI_PATTERN
from key_words_lib import (
    build_keywords_library,
    generate_citations_csv,
    compare_csv_with_library,
    CSV_PATH,
)
from browser import find_and_download_pdf
from calling_llm_reader import (
    get_pdf_links,
    download_pdf,
    extract_text,
    summarize_and_save,
    log_session_start,
    process_local_pdf,
)
from token_guard import TokenLimitError
from summarizer import generate_daily_report

ROOT            = Path(__file__).parent.parent
BASE_PAPERS_DIR = ROOT / "base_papers"
CACHE_DIR       = ROOT / "pdf_cache"

TOP_N = 10

# ── Helpers ───────────────────────────────────────────────────────────────────

def now() -> datetime:
    return datetime.now()

def is_within_window(deadline: datetime) -> bool:
    return now() < deadline

def seconds_until(hour: int) -> float:
    target = now().replace(hour=hour, minute=0, second=0, microsecond=0)
    if target <= now():
        target += timedelta(days=1)
    return (target - now()).total_seconds()

def wait_until_start():
    secs = seconds_until(1)
    wake = now() + timedelta(seconds=secs)
    print(f"[timer] Waiting until {wake.strftime('%Y-%m-%d %H:%M')} to start ... ({secs/3600:.1f}h)")
    time.sleep(secs)

def clear_pdf_cache():
    pdfs = list(CACHE_DIR.glob("*.pdf"))
    for pdf in pdfs:
        pdf.unlink()
    print(f"[timer] Cleared {len(pdfs)} PDF(s) from pdf_cache/")

def delete_csv():
    if CSV_PATH.exists():
        CSV_PATH.unlink()
        print(f"[timer] Deleted {CSV_PATH.name}")

# ── Load DOI list from base_papers/base_papers.txt ───────────────────────────

DOI_LIST_PATH = BASE_PAPERS_DIR / "base_papers.txt"

def load_doi_list() -> list[tuple[str, str]] | None:
    """
    Read base_papers/base_papers.txt if it exists.
    Each non-blank, non-comment line is treated as a DOI.
    Returns a list of (doi, "") pairs, or None if the file doesn't exist.
    """
    if not DOI_LIST_PATH.exists():
        return None
    dois = []
    for line in DOI_LIST_PATH.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            dois.append(line)
    if not dois:
        print(f"[timer] {DOI_LIST_PATH.name} exists but contains no DOIs — falling back to PDF scan.")
        return None
    print(f"[timer] Loaded {len(dois)} DOI(s) from {DOI_LIST_PATH.name}")
    return [(doi, "") for doi in dois]

# ── Pair DOI + title per base paper ──────────────────────────────────────────

def get_base_paper_items() -> list[tuple[str, str]]:
    """
    For each PDF in base_papers/, return (doi, title).
    DOI is extracted via regex; title is extracted via Claude.
    Either may be empty if extraction fails.
    """
    items: list[tuple[str, str]] = []
    for pdf in sorted(BASE_PAPERS_DIR.glob("*.pdf")):
        text = extract_pdf_text(pdf)
        matches = DOI_PATTERN.findall(text[:3000]) if text else []
        doi = matches[0] if matches else ""
        title = TitleExtractor.extract_title(pdf)
        print(f"  {pdf.name} → doi={doi or '(none)'}, title={title[:70]!r}")
        items.append((doi, title))
    return items

# ── Process a single paper: doi-first, title-fallback ────────────────────────

def process_item(doi: str, title: str, deadline: datetime) -> bool:
    """
    Try to download and summarize a paper.
    Attempts the DOI path first; falls back to title-based browser search if
    the DOI is missing or the download fails.
    Returns True if a summary was produced.
    """
    if not is_within_window(deadline):
        return False

    label = doi or title
    print(f"\n  Processing: {label}")
    log_session_start(label)

    # ── DOI path ──────────────────────────────────────────────────────────────
    if doi:
        try:
            fetched_title, pdf_urls = get_pdf_links(doi)
            pdf_path = download_pdf(pdf_urls, doi)
            if pdf_path:
                text = extract_text(pdf_path)
                if text:
                    summarize_and_save(fetched_title or title, doi, text)
                    return True
            print(f"  [WARN] DOI path yielded no PDF for {doi} — trying title fallback.")
        except Exception as e:
            print(f"  [WARN] DOI path failed for {doi}: {e} — trying title fallback.")

    # ── Title fallback ────────────────────────────────────────────────────────
    if title:
        try:
            pdf_path = find_and_download_pdf(title)
            if pdf_path:
                text = extract_text(pdf_path)
                if text:
                    summarize_and_save(title, doi or title, text)
                    return True
        except Exception as e:
            print(f"  [ERROR] Title path failed for {title!r}: {e}")

    print(f"  [SKIP] Could not process: {label}")
    return False

# ── Process a list of (doi, title) pairs ─────────────────────────────────────

def process_items(items: list[tuple[str, str]], deadline: datetime):
    if not items:
        print("[timer] No items to process.")
        return

    print(f"\n[timer] Processing {len(items)} paper(s) ...")
    for i, (doi, title) in enumerate(items, 1):
        if not is_within_window(deadline):
            print(f"\n[timer] Deadline reached — stopping early.")
            return
        print(f"\n  [{i}/{len(items)}]")
        process_item(doi, title, deadline)

# ── Main flow ─────────────────────────────────────────────────────────────────

def run(deadline: datetime):
    print(f"\n[timer] Session started at {now().strftime('%H:%M:%S')} — deadline {deadline.strftime('%H:%M:%S')}")

    # ── Build keyword library (from base_papers/) ────────────────────────────
    _, all_kws = build_keywords_library()
    if not all_kws:
        print("[timer] Keywords library empty — cannot run comparisons.")
        return

    # ── Initialization: process base papers ──────────────────────────────────
    print("\n[timer] Init — processing base papers ...")
    base_items = load_doi_list()
    if base_items is not None:
        print(f"[timer] Using base_papers.txt DOI list ({len(base_items)} DOI(s)) — skipping PDF scan.")
    else:
        print("[timer] No base_papers.txt found — scanning PDFs in base_papers/.")
        base_items = get_base_paper_items()
    process_items(base_items, deadline)
    clear_pdf_cache()

    # ── First discovery: citations from base_papers/ ─────────────────────────
    generate_citations_csv(BASE_PAPERS_DIR, CSV_PATH)
    results = compare_csv_with_library(CSV_PATH, all_kws, top_n=TOP_N)
    related_items = [(doi, title) for doi, title, _, _ in results]
    delete_csv()

    # ── Loop: discover → process → discover ... ───────────────────────────────
    iteration = 1
    try:
        while is_within_window(deadline) and related_items:
            print(f"\n[timer] Loop iteration {iteration} ({now().strftime('%H:%M')}) — {len(related_items)} paper(s)")
            process_items(related_items, deadline)
            generate_citations_csv(CACHE_DIR, CSV_PATH)
            results = compare_csv_with_library(CSV_PATH, all_kws, top_n=TOP_N)
            related_items = [(doi, title) for doi, title, _, _ in results]
            clear_pdf_cache()
            delete_csv()
            iteration += 1
    except TokenLimitError as e:
        print(f"\n[timer] Token limit reached — stopping pipeline early. ({e})")

    # ── Generate daily report (always, even after early stop) ────────────────
    print(f"\n[timer] Window closed at {now().strftime('%H:%M')}. Generating daily report ...")
    generate_daily_report()
    print("\n[timer] All done.")

# ── Local mode ────────────────────────────────────────────────────────────────

def run_local():
    """Process every PDF in base_papers/ directly, then generate the daily report."""
    pdfs = sorted(BASE_PAPERS_DIR.glob("*.pdf"))
    if not pdfs:
        print("[timer] No PDFs found in base_papers/ — nothing to process.")
        return

    print(f"[timer] Local mode — processing {len(pdfs)} PDF(s) from base_papers/ ...")
    for i, pdf in enumerate(pdfs, 1):
        print(f"\n  [{i}/{len(pdfs)}] {pdf.name}")
        try:
            process_local_pdf(pdf)
        except Exception as e:
            print(f"  [ERROR] {pdf.name}: {e}")

    print(f"\n[timer] Done processing. Generating daily report ...")
    generate_daily_report()
    print("\n[timer] All done.")

def main():
    parser = argparse.ArgumentParser(description="Reportea pipeline orchestrator")
    parser.add_argument(
        "--now", metavar="HOURS", nargs="?", const=1, type=float,
        help="Start immediately and run for HOURS hours (default 1). Skips the 01:00 wait."
    )
    parser.add_argument(
        "--local", action="store_true",
        help="Summarize all PDFs in base_papers/ directly, then generate the daily report."
    )
    args = parser.parse_args()

    try:
        if args.local:
            run_local()
        elif args.now is not None:
            deadline = now() + timedelta(hours=args.now)
            print(f"[timer] Immediate mode — running for {args.now}h until {deadline.strftime('%H:%M:%S')}")
            run(deadline)
        else:
            wait_until_start()
            deadline = now().replace(hour=3, minute=0, second=0, microsecond=0)
            run(deadline)
    except KeyboardInterrupt:
        print("\n[timer] Interrupted by user.")

if __name__ == "__main__":
    main()
