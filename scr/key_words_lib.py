"""
key_words_lib.py

Keyword library management and comparison:
  - build_keywords_library()    : extract keywords from base_papers/ → library
  - generate_citations_csv()    : citation DOIs → keywords → keywords_list.csv
  - compare_csv_with_library()  : score each CSV row against library, return top-N DOIs
"""

import csv
import subprocess
from pathlib import Path

from extractor import extract_pdf_text, KeywordExtractor, CitationExtractor

CLAUDE_BIN = "/Users/mac/.vscode/extensions/anthropic.claude-code-2.1.87-darwin-x64/resources/native-binary/claude"

ROOT            = Path(__file__).parent.parent
BASE_PAPERS_DIR = ROOT / "base_papers"
CACHE_DIR       = ROOT / "pdf_cache"
CSV_PATH        = ROOT / "keywords_list.csv"

# ── Build library ─────────────────────────────────────────────────────────────

def build_keywords_library() -> tuple[dict[str, set[str]], set[str]]:
    if not BASE_PAPERS_DIR.exists():
        BASE_PAPERS_DIR.mkdir()
        print(f"  Created empty base_papers/ at {BASE_PAPERS_DIR}")
        return {}, set()

    pdfs = list(BASE_PAPERS_DIR.glob("*.pdf"))
    if not pdfs:
        print("  No PDFs found in base_papers/.")
        return {}, set()

    print(f"\n[keywords] Building library from {len(pdfs)} base paper(s) ...")
    per_paper: dict[str, set[str]] = {}
    all_kws: set[str] = set()

    for pdf in pdfs:
        text = extract_pdf_text(pdf)
        if not text:
            continue
        raw = KeywordExtractor.from_text(text, pdf.name)
        kws = KeywordExtractor.normalize(raw)
        per_paper[pdf.name] = kws
        all_kws |= kws

    print(f"  Library: {len(all_kws)} unique keywords from {len(per_paper)} paper(s).")
    return per_paper, all_kws

# ── Fetch keywords for a single DOI ──────────────────────────────────────────

def _fetch_keywords_for_doi(doi: str) -> set[str]:
    result = subprocess.run(
        [CLAUDE_BIN, "-p",
         f"Look up the academic paper with DOI: {doi}. "
         "Find the author-defined keywords. "
         "Return ONLY a comma-separated list of keywords, nothing else. "
         "If you cannot find keywords, return an empty response.",
         "--allowedTools", "WebFetch,WebSearch"],
        capture_output=True, text=True
    )
    raw = [kw.strip() for kw in result.stdout.strip().split(",") if kw.strip()]
    return KeywordExtractor.normalize(raw)

# ── Generate citations CSV ────────────────────────────────────────────────────

def generate_citations_csv(source_dir: Path, csv_path: Path) -> int:
    """
    For every PDF in source_dir:
      1. Extract + validate its citation DOIs via CitationExtractor
      2. Fetch keywords for each DOI via Claude (web search)
      3. Write to csv_path:
            keywords (pipe-separated)  |  doi

    Returns the number of rows written.

    CSV format:
        keywords,doi
        keyword1|keyword2|keyword3,10.xxxx/yyyy
    """
    # Collect unique citation DOIs from all PDFs in source_dir
    all_dois: list[str] = []
    for pdf in sorted(source_dir.glob("*.pdf")):
        dois = CitationExtractor.extract_and_cache(pdf)
        all_dois.extend(dois)
    unique_dois = list(dict.fromkeys(all_dois))

    if not unique_dois:
        print(f"  No valid cited DOIs found in {source_dir.name}/")
        return 0

    print(f"\n[keywords] Fetching keywords for {len(unique_dois)} citation DOI(s) ...")
    rows: list[tuple[str, str]] = []
    for i, doi in enumerate(unique_dois, 1):
        print(f"  [{i}/{len(unique_dois)}] {doi}")
        kws = _fetch_keywords_for_doi(doi)
        if kws:
            rows.append(("|".join(sorted(kws)), doi))

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["keywords", "doi"])
        writer.writerows(rows)

    print(f"  Wrote {len(rows)} rows → {csv_path.name}")
    return len(rows)

# ── Compare CSV against library ───────────────────────────────────────────────

def compare_csv_with_library(
    csv_path: Path,
    all_kws: set[str],
    top_n: int = 10,
) -> list[tuple[str, int, set[str]]]:
    """
    Read keywords_list.csv (columns: keywords, doi).
    Score each row's keywords against all_kws.
    Returns list of (doi, overlap_count, matched_keywords)
    sorted by overlap_count descending, capped at top_n.
    """
    if not all_kws:
        print("  Keywords library is empty — nothing to compare against.")
        return []

    if not csv_path.exists():
        print(f"  {csv_path.name} not found.")
        return []

    scores: list[tuple[str, int, set[str]]] = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            doi = row.get("doi", "").strip()
            kws_raw = row.get("keywords", "")
            if not doi or not kws_raw:
                continue
            kws = KeywordExtractor.normalize(kws_raw.split("|"))
            overlap = kws & all_kws
            if overlap:
                scores.append((doi, len(overlap), overlap))

    scores.sort(key=lambda x: x[1], reverse=True)
    top = scores[:top_n]

    print(f"\n[keywords] {len(scores)} matches → returning top {len(top)}:")
    for rank, (doi, score, matched) in enumerate(top, 1):
        print(f"  {rank:2}. [{score}] {doi}  ({', '.join(sorted(matched))})")

    return top

# ── Main ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    try:
        _, all_kws = build_keywords_library()
        if not all_kws:
            print("\nAdd PDFs to base_papers/ and re-run.")
            sys.exit(0)

        source = Path(sys.argv[1]) if len(sys.argv) > 1 else BASE_PAPERS_DIR
        generate_citations_csv(source, CSV_PATH)
        results = compare_csv_with_library(CSV_PATH, all_kws, top_n=10)

        if results:
            print("\n── Top related DOIs ──")
            for rank, (doi, score, matched) in enumerate(results, 1):
                print(f"  {rank:2}. [{score}] {doi}")
        else:
            print("\nNo overlapping papers found.")

    except KeyboardInterrupt:
        print("\n[Interrupted]")
