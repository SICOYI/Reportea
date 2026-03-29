"""
extractor.py

Three extraction modules in one file:

  Module 1 — DOIExtractor
      Extract a paper's own DOI from PDFs in base_papers/

  Module 2 — KeywordExtractor
      Extract and normalize author-defined keywords from paper text via Claude

  Module 3 — CitationExtractor
      Extract cited DOIs from a PDF's references, validate via doi.org, cache to doi_cache/
"""

import re
import json
import subprocess
import requests
from pathlib import Path

CLAUDE_BIN = "/Users/mac/.vscode/extensions/anthropic.claude-code-2.1.87-darwin-x64/resources/native-binary/claude"

ROOT            = Path(__file__).parent.parent
BASE_PAPERS_DIR = ROOT / "base_papers"
CACHE_DIR       = ROOT / "pdf_cache"
DOI_CACHE_DIR   = ROOT / "doi_cache"

DOI_PATTERN = re.compile(
    r'\b(10\.\d{4,9}/[-._;()/:A-Za-z0-9]+)',
    re.IGNORECASE
)

# ── Shared: PDF text ──────────────────────────────────────────────────────────

def extract_pdf_text(pdf_path: Path) -> str:
    try:
        import pdfplumber
        with pdfplumber.open(pdf_path) as pdf:
            return "\n".join(page.extract_text() or "" for page in pdf.pages)
    except ImportError:
        print("  ERROR: pip install pdfplumber")
        return ""
    except Exception as e:
        print(f"  Failed to read {pdf_path.name}: {e}")
        return ""


# ════════════════════════════════════════════════════════════
# Module 1 — DOIExtractor
# ════════════════════════════════════════════════════════════

class DOIExtractor:
    """Extract each paper's own DOI from PDFs in base_papers/."""

    @staticmethod
    def get_dois_from_base_papers() -> list[str]:
        if not BASE_PAPERS_DIR.exists() or not list(BASE_PAPERS_DIR.glob("*.pdf")):
            print("  base_papers/ is empty or missing.")
            return []

        dois: list[str] = []
        for pdf in sorted(BASE_PAPERS_DIR.glob("*.pdf")):
            text = extract_pdf_text(pdf)
            matches = DOI_PATTERN.findall(text[:3000])
            if matches:
                doi = matches[0]
                print(f"  {pdf.name} → {doi}")
                dois.append(doi)
            else:
                print(f"  {pdf.name} → DOI not found (skipping)")
        return dois


# ════════════════════════════════════════════════════════════
# Module 2 — KeywordExtractor
# ════════════════════════════════════════════════════════════

class KeywordExtractor:
    """Extract and normalize author-defined keywords from paper text via Claude."""

    @staticmethod
    def normalize(raw: list[str]) -> set[str]:
        return {kw.strip().lower().strip(".,;:") for kw in raw if kw.strip()}

    @staticmethod
    def from_text(text: str, filename: str) -> list[str]:
        result = subprocess.run(
            [CLAUDE_BIN, "-p",
             "From the following academic paper text, extract the author-defined keywords. "
             "Return ONLY a comma-separated list of keywords, nothing else.\n\n" + text[:8000]],
            capture_output=True, text=True
        )
        keywords = [kw.strip() for kw in result.stdout.strip().split(",") if kw.strip()]
        print(f"    [{filename}] → {len(keywords)} keywords")
        return keywords

    @classmethod
    def from_pdf(cls, pdf_path: Path) -> set[str]:
        text = extract_pdf_text(pdf_path)
        if not text:
            return set()
        return cls.normalize(cls.from_text(text, pdf_path.name))


# ════════════════════════════════════════════════════════════
# Module 3 — CitationExtractor
# ════════════════════════════════════════════════════════════

class CitationExtractor:
    """Extract cited DOIs from a PDF's references, validate, and cache."""

    @staticmethod
    def _is_resolvable(doi: str) -> bool:
        try:
            r = requests.head(
                f"https://doi.org/{doi}",
                timeout=8,
                allow_redirects=True,
                headers={"User-Agent": "Mozilla/5.0 (research bot)"}
            )
            return r.status_code < 400
        except Exception:
            return False

    @classmethod
    def extract_and_cache(cls, pdf_path: Path) -> list[str]:
        """
        Extract cited DOIs from references, validate via doi.org,
        cache to doi_cache/<pdf_stem>_cited_dois.json.
        Returns valid DOIs.
        """
        DOI_CACHE_DIR.mkdir(exist_ok=True)
        cache_file = DOI_CACHE_DIR / f"{pdf_path.stem}_cited_dois.json"

        if cache_file.exists():
            cached = json.loads(cache_file.read_text(encoding="utf-8"))
            print(f"  {pdf_path.name} → {len(cached)} cached cited DOIs loaded")
            return cached

        text = extract_pdf_text(pdf_path)
        ref_match = re.search(r'(?i)\breferences\b', text)
        section = text[ref_match.start():] if ref_match else text

        raw_dois = list(dict.fromkeys(DOI_PATTERN.findall(section)))
        print(f"  {pdf_path.name} → {len(raw_dois)} raw cited DOIs, validating ...")

        valid: list[str] = []
        for i, doi in enumerate(raw_dois, 1):
            ok = cls._is_resolvable(doi)
            print(f"    [{i}/{len(raw_dois)}] {'✓' if ok else '✗'} {doi}")
            if ok:
                valid.append(doi)

        cache_file.write_text(json.dumps(valid, indent=2), encoding="utf-8")
        print(f"  Cached {len(valid)} valid DOIs → {cache_file.name}")
        return valid

    @staticmethod
    def get_all_cached() -> list[str]:
        """Aggregate all valid cited DOIs across every cache file in doi_cache/."""
        if not DOI_CACHE_DIR.exists():
            return []
        all_dois: list[str] = []
        for f in sorted(DOI_CACHE_DIR.glob("*_cited_dois.json")):
            all_dois.extend(json.loads(f.read_text(encoding="utf-8")))
        return list(dict.fromkeys(all_dois))
