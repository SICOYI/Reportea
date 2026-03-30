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

import argparse
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from extractor import DOIExtractor, TitleExtractor
from key_words_lib import (
    build_keywords_library,
    generate_citations_csv,
    generate_citations_csv_titles,
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

# ── Process a list of DOIs ────────────────────────────────────────────────────

def process_dois(dois: list[str], deadline: datetime):
    if not dois:
        print("[timer] No DOIs to process.")
        return

    print(f"\n[timer] Processing {len(dois)} DOI(s) ...")
    for i, doi in enumerate(dois, 1):
        if not is_within_window(deadline):
            print(f"\n[timer] Deadline reached — stopping early.")
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

# ── Process a list of titles (title-based fallback) ───────────────────────────

def process_titles(titles: list[str], deadline: datetime):
    if not titles:
        print("[timer] No titles to process.")
        return

    print(f"\n[timer] Processing {len(titles)} title(s) via browser ...")
    for i, title in enumerate(titles, 1):
        if not is_within_window(deadline):
            print(f"\n[timer] Deadline reached — stopping early.")
            return
        print(f"\n  [{i}/{len(titles)}] {title}")
        try:
            log_session_start(title)
            pdf_path = find_and_download_pdf(title)
            if pdf_path:
                text = extract_text(pdf_path)
                if text:
                    summarize_and_save(title, title, text)
        except Exception as e:
            print(f"  [ERROR] {title}: {e}")

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
    base_dois = DOIExtractor.get_dois_from_base_papers()

    if base_dois:
        use_title_mode = False
        process_dois(base_dois, deadline)
        clear_pdf_cache()
        n = generate_citations_csv(BASE_PAPERS_DIR, CSV_PATH)
        if n == 0:
            print("[timer] No citation DOIs found — falling back to title-based citation discovery.")
            use_title_mode = True
            generate_citations_csv_titles(BASE_PAPERS_DIR, CSV_PATH)
    else:
        use_title_mode = True
        print("[timer] No DOIs found — switching to title-based mode.")
        base_titles = TitleExtractor.extract_titles_from_dir(BASE_PAPERS_DIR)
        process_titles(base_titles, deadline)
        clear_pdf_cache()
        generate_citations_csv_titles(BASE_PAPERS_DIR, CSV_PATH)

    results = compare_csv_with_library(CSV_PATH, all_kws, top_n=TOP_N)
    related_items = [item for item, _, _ in results]
    delete_csv()

    # ── Loop: discover → process → discover ... ───────────────────────────────
    iteration = 1
    while is_within_window(deadline) and related_items:
        mode_label = "title(s)" if use_title_mode else "DOI(s)"
        print(f"\n[timer] Loop iteration {iteration} ({now().strftime('%H:%M')}) — {len(related_items)} {mode_label}")

        if use_title_mode:
            process_titles(related_items, deadline)
            generate_citations_csv_titles(CACHE_DIR, CSV_PATH)
        else:
            process_dois(related_items, deadline)
            n = generate_citations_csv(CACHE_DIR, CSV_PATH)
            if n == 0:
                print("[timer] No citation DOIs found — falling back to title-based citation discovery.")
                use_title_mode = True
                generate_citations_csv_titles(CACHE_DIR, CSV_PATH)

        results = compare_csv_with_library(CSV_PATH, all_kws, top_n=TOP_N)
        related_items = [item for item, _, _ in results]

        clear_pdf_cache()
        delete_csv()
        iteration += 1

    # ── Generate daily report ────────────────────────────────────────────────
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
            deadline = now().replace(hour=4, minute=0, second=0, microsecond=0)
            run(deadline)
    except KeyboardInterrupt:
        print("\n[timer] Interrupted by user.")

if __name__ == "__main__":
    main()
