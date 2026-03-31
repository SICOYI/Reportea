#!/usr/bin/env python3
"""
clean.py — wipe generated artefacts.

Default (no flags):
    Clears only transient cache files that are regenerated each run:
        pdf_cache/*.pdf
        doi_cache/*.json
        keywords_list.csv

--all:
    Also clears persistent output files:
        summaries/*.md
        claude_responses.log
"""

import argparse
from pathlib import Path

ROOT        = Path(__file__).parent.parent
PDF_CACHE   = ROOT / "pdf_cache"
DOI_CACHE   = ROOT / "doi_cache"
SUMMARIES   = ROOT / "summaries"
LOG_FILE    = ROOT / "claude_responses.log"
CSV_FILE    = ROOT / "keywords_list.csv"


def _clear_dir(path: Path, pattern: str = "*") -> int:
    count = 0
    for f in path.glob(pattern):
        f.unlink()
        count += 1
    return count


def clean_cache():
    """Clear only transient cache files (safe to run between pipeline runs)."""
    n_pdf = _clear_dir(PDF_CACHE, "*.pdf")  if PDF_CACHE.exists()  else 0
    n_doi = _clear_dir(DOI_CACHE, "*.json") if DOI_CACHE.exists()  else 0
    CSV_FILE.unlink(missing_ok=True)

    print(f"[clean] pdf_cache : {n_pdf} file(s) removed")
    print(f"[clean] doi_cache : {n_doi} file(s) removed")
    print(f"[clean] keywords_list.csv removed (if existed)")


def clean_all():
    """Clear cache AND all generated outputs (summaries + log)."""
    clean_cache()

    n_sum = _clear_dir(SUMMARIES, "*.md") if SUMMARIES.exists() else 0
    print(f"[clean] summaries : {n_sum} file(s) removed")

    if LOG_FILE.exists():
        LOG_FILE.unlink()
        print(f"[clean] claude_responses.log removed")

    print("[clean] Done.")


def main():
    parser = argparse.ArgumentParser(description="Clean Reportea generated files.")
    parser.add_argument(
        "--all", action="store_true",
        help="Also remove summaries/*.md and claude_responses.log (default: cache only)"
    )
    args = parser.parse_args()

    if args.all:
        clean_all()
    else:
        clean_cache()
        print("[clean] Done. (run with --all to also clear summaries and log)")


if __name__ == "__main__":
    main()
