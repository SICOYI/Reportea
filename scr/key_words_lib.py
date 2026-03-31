"""
key_words_lib.py

Keyword library management and comparison:
  - build_keywords_library()    : extract keywords from base_papers/ → library
  - generate_citations_csv()    : citation DOIs + titles → keywords → keywords_list.csv
  - compare_csv_with_library()  : score each CSV row against library, return top-N (doi, title) pairs
"""

import csv
import subprocess
from pathlib import Path

from extractor import extract_pdf_text, KeywordExtractor, CitationExtractor, TitleExtractor

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

# ── Fetch keywords for a single title ────────────────────────────────────────

def _fetch_keywords_for_title(title: str) -> set[str]:
    result = subprocess.run(
        [CLAUDE_BIN, "-p",
         f'Look up the academic paper titled: "{title}". '
         "Find the author-defined keywords. "
         "Return ONLY a comma-separated list of keywords, nothing else. "
         "If you cannot find keywords, return an empty response.",
         "--allowedTools", "WebFetch,WebSearch"],
        capture_output=True, text=True
    )
    raw = [kw.strip() for kw in result.stdout.strip().split(",") if kw.strip()]
    return KeywordExtractor.normalize(raw)

# ── Generate unified citations CSV (DOI + title, 3 columns) ──────────────────

def generate_citations_csv(source_dir: Path, csv_path: Path) -> int:
    """
    For every PDF in source_dir, run both CitationExtractor (DOIs) and
    TitleExtractor (titles) on the references section.

    For each unique DOI found: fetch keywords → row (keywords, doi, "")
    For each unique title found: fetch keywords → row (keywords, "", title)

    Writes to csv_path with 3 columns: keywords, doi, title
    Returns the number of rows written.

    CSV format:
        keywords,doi,title
        keyword1|keyword2|keyword3,10.xxxx/yyyy,
        keyword1|keyword2|keyword3,,Some Paper Title
    """
    all_dois: list[str] = []
    all_titles: list[str] = []

    for pdf in sorted(source_dir.glob("*.pdf")):
        dois = CitationExtractor.extract_and_cache(pdf)
        all_dois.extend(dois)
        titles = TitleExtractor.extract_citation_titles(pdf)
        all_titles.extend(titles)

    unique_dois   = list(dict.fromkeys(all_dois))
    unique_titles = list(dict.fromkeys(all_titles))

    if not unique_dois and not unique_titles:
        print(f"  No citation DOIs or titles found in {source_dir.name}/")
        return 0

    print(f"\n[keywords] {len(unique_dois)} citation DOI(s), {len(unique_titles)} citation title(s) found.")

    rows: list[tuple[str, str, str]] = []

    if unique_dois:
        print(f"[keywords] Fetching keywords for {len(unique_dois)} DOI(s) ...")
        for i, doi in enumerate(unique_dois, 1):
            print(f"  [{i}/{len(unique_dois)}] {doi}")
            kws = _fetch_keywords_for_doi(doi)
            if kws:
                rows.append(("|".join(sorted(kws)), doi, ""))

    if unique_titles:
        print(f"[keywords] Fetching keywords for {len(unique_titles)} title(s) ...")
        for i, title in enumerate(unique_titles, 1):
            print(f"  [{i}/{len(unique_titles)}] {title}")
            kws = _fetch_keywords_for_title(title)
            if kws:
                rows.append(("|".join(sorted(kws)), "", title))

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["keywords", "doi", "title"])
        writer.writerows(rows)

    print(f"  Wrote {len(rows)} rows → {csv_path.name}")
    return len(rows)

# ── Compare CSV against library ───────────────────────────────────────────────

def compare_csv_with_library(
    csv_path: Path,
    all_kws: set[str],
    top_n: int = 10,
) -> list[tuple[str, str, int, set[str]]]:
    """
    Read keywords_list.csv (3 columns: keywords, doi, title).
    Score each row's keywords against all_kws.
    Returns list of (doi, title, overlap_count, matched_keywords)
    sorted by overlap_count descending, capped at top_n.
    """
    if not all_kws:
        print("  Keywords library is empty — nothing to compare against.")
        return []

    if not csv_path.exists():
        print(f"  {csv_path.name} not found.")
        return []

    scores: list[tuple[str, str, int, set[str]]] = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            doi   = row.get("doi",   "").strip()
            title = row.get("title", "").strip()
            kws_raw = row.get("keywords", "")
            if not doi and not title:
                continue
            kws = KeywordExtractor.normalize(kws_raw.split("|")) if kws_raw else set()
            overlap = kws & all_kws
            scores.append((doi, title, len(overlap), overlap))

    scores.sort(key=lambda x: x[2], reverse=True)
    top = scores[:top_n]

    matched_count = sum(1 for _, _, s, _ in scores if s > 0)
    print(f"\n[keywords] {matched_count} keyword match(es) among {len(scores)} — returning top {len(top)}:")
    for rank, (doi, title, score, matched) in enumerate(top, 1):
        label = doi or title
        kw_label = f"({', '.join(sorted(matched))})" if matched else "(no keyword overlap)"
        print(f"  {rank:2}. [{score}] {label}  {kw_label}")

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
            print("\n── Top related papers ──")
            for rank, (doi, title, score, matched) in enumerate(results, 1):
                label = doi or title
                print(f"  {rank:2}. [{score}] {label}")
        else:
            print("\nNo overlapping papers found.")

    except KeyboardInterrupt:
        print("\n[Interrupted]")
