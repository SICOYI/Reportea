"""
timer.py  —  Main orchestrator for Reportea

Schedule:
  01:00  Wake up

         Initialization
           ├── Build keywords library from base_papers/
           ├── Extract base paper DOIs → process via calling_llm_reader
           ├── Clear pdf_cache/
           ├── Generate keywords_list.csv from base_papers/ citations
           ├── Compare CSV against library → top-10 related DOIs
           └── Delete keywords_list.csv

         Loop  (repeats until 04:00)
           ├── Process related DOIs via calling_llm_reader
           ├── Generate keywords_list.csv from pdf_cache/ citations
           ├── Compare CSV against library → next top-10 DOIs
           ├── Clear pdf_cache/
           └── Delete keywords_list.csv

  04:00  Generate daily digest via summarizer
"""

import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from extractor import DOIExtractor
from key_words_lib import (
    build_keywords_library,
    generate_citations_csv,
    compare_csv_with_library,
    CSV_PATH,
)
from calling_llm_reader import (
    get_pdf_links,
    download_pdf,
    extract_text,
    summarize_and_save,
    log_session_start,
)
from summarizer import generate_daily_report

ROOT            = Path(__file__).parent.parent
BASE_PAPERS_DIR = ROOT / "base_papers"
CACHE_DIR       = ROOT / "pdf_cache"

START_HOUR = 1    # 01:00
END_HOUR   = 4    # 04:00
TOP_N      = 10

# ── Helpers ───────────────────────────────────────────────────────────────────

def now() -> datetime:
    return datetime.now()

def is_within_window() -> bool:
    return START_HOUR <= now().hour < END_HOUR

def seconds_until(hour: int) -> float:
    target = now().replace(hour=hour, minute=0, second=0, microsecond=0)
    if target <= now():
        target += timedelta(days=1)
    return (target - now()).total_seconds()

def wait_until_start():
    if is_within_window():
        print(f"[timer] Already within window ({now().strftime('%H:%M')}). Starting now.")
        return
    secs = seconds_until(START_HOUR)
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

# ── Process a list of DOIs ────────────────────────────────────────────────────

def process_dois(dois: list[str]):
    if not dois:
        print("[timer] No DOIs to process.")
        return

    print(f"\n[timer] Processing {len(dois)} DOI(s) ...")
    for i, doi in enumerate(dois, 1):
        if not is_within_window():
            print(f"\n[timer] Past {END_HOUR}:00 — stopping early.")
            return
        print(f"\n  [{i}/{len(dois)}] {doi}")
        try:
            log_session_start(doi)
            title, pdf_urls = get_pdf_links(doi)
            pdf_path = download_pdf(pdf_urls, doi)
            if pdf_path:
                text = extract_text(pdf_path)
                if text:
                    summarize_and_save(title, doi, text)
        except Exception as e:
            print(f"  [ERROR] {doi}: {e}")

# ── Main flow ─────────────────────────────────────────────────────────────────

def run():
    wait_until_start()
    print(f"\n[timer] Session started at {now().strftime('%H:%M:%S')}")

    # ── Build keyword library (from base_papers/) ────────────────────────────
    _, all_kws = build_keywords_library()
    if not all_kws:
        print("[timer] Keywords library empty — cannot run comparisons.")
        return

    # ── Initialization: process base papers ──────────────────────────────────
    print("\n[timer] Init — processing base papers ...")
    base_dois = DOIExtractor.get_dois_from_base_papers()
    process_dois(base_dois)
    clear_pdf_cache()

    # Build initial CSV from base_papers/ citations, get first batch of DOIs
    generate_citations_csv(BASE_PAPERS_DIR, CSV_PATH)
    results = compare_csv_with_library(CSV_PATH, all_kws, top_n=TOP_N)
    related_dois = [doi for doi, _, _ in results]
    delete_csv()

    # ── Loop: discover → process → discover ... ───────────────────────────────
    iteration = 1
    while is_within_window() and related_dois:
        print(f"\n[timer] Loop iteration {iteration} ({now().strftime('%H:%M')}) — {len(related_dois)} DOI(s)")

        process_dois(related_dois)

        generate_citations_csv(CACHE_DIR, CSV_PATH)
        results = compare_csv_with_library(CSV_PATH, all_kws, top_n=TOP_N)
        related_dois = [doi for doi, _, _ in results]

        clear_pdf_cache()
        delete_csv()
        iteration += 1

    # ── Generate daily report ────────────────────────────────────────────────
    print(f"\n[timer] Window closed at {now().strftime('%H:%M')}. Generating daily report ...")
    generate_daily_report()
    print("\n[timer] All done.")

if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        print("\n[timer] Interrupted by user.")
