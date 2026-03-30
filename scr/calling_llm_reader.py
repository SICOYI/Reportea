import subprocess
import requests
import re
from datetime import datetime
from pathlib import Path

# ls ~/.vscode/extensions/ | grep anthropic  →  update version below if binary not found
CLAUDE_BIN = "/Users/mac/.vscode/extensions/anthropic.claude-code-2.1.87-darwin-x64/resources/native-binary/claude"

ROOT       = Path(__file__).parent.parent
CACHE_DIR  = ROOT / "pdf_cache"
OUTPUT_DIR = ROOT / "summaries"
LOG_FILE   = ROOT / "claude_responses.log"

DOI = "10.1109/IPDPSW63119.2024.00101"

# ── Helpers ──────────────────────────────────────────────────────────────────

def call_claude(prompt: str, allow_web: bool = True) -> str:
    args = [CLAUDE_BIN, "-p", prompt]
    if allow_web:
        args += ["--allowedTools", "WebFetch,WebSearch"]
    result = subprocess.run(args, capture_output=True, text=True)
    return result.stdout.strip()

def log_session_start(doi: str):
    with open(LOG_FILE, "a") as f:
        f.write("\n" + "=" * 60 + "\n")
        f.write(f"SESSION START  {datetime.now().isoformat()}\n")
        f.write(f"DOI: {doi}\n")
        f.write("=" * 60 + "\n")

def log(label: str, content: str):
    with open(LOG_FILE, "a") as f:
        f.write(f"[{datetime.now().isoformat()}] {label}\n")
        f.write(content + "\n")
        f.write("-" * 60 + "\n")

def extract_urls(text: str) -> list[str]:
    return re.findall(r'https?://[^\s\)\]\"\']+', text)

def safe_doi(doi: str) -> str:
    return doi.replace("/", "_").replace(".", "-")

# ── Step 1: Find PDF links ────────────────────────────────────────────────────

def get_pdf_links(doi: str) -> tuple[str, list[str]]:
    print(f"\n[1/4] Searching for PDF links for DOI: {doi} ...")
    prompt = (
        f"Look up the paper with DOI: {doi}. "
        "Retrieve the paper title. "
        "Then search for freely available PDF versions on Semantic Scholar, "
        "Unpaywall (unpaywall.org), ResearchGate, and the publisher page. "
        "Return: 1) the paper title, 2) every direct PDF URL you find. "
        "List each URL on its own line prefixed with 'PDF_URL:'."
    )
    response = call_claude(prompt, allow_web=True)
    log("STEP 1 - PDF search", response)

    title_match = re.search(r'(?i)title[:\-]\s*(.+)', response)
    title = title_match.group(1).strip() if title_match else doi.replace("/", "_")

    pdf_urls = re.findall(r'PDF_URL:\s*(https?://[^\s]+)', response)
    if not pdf_urls:
        pdf_urls = [u for u in extract_urls(response) if "pdf" in u.lower()]

    print(f"    Title : {title}")
    print(f"    PDFs  : {pdf_urls if pdf_urls else 'None found'}")
    return title, pdf_urls

# ── Step 2: Download & cache PDF ─────────────────────────────────────────────

def download_pdf(pdf_urls: list[str], doi: str) -> Path | None:
    CACHE_DIR.mkdir(exist_ok=True)
    dest = CACHE_DIR / f"{safe_doi(doi)}.pdf"

    if dest.exists():
        print(f"\n[2/4] PDF already cached: {dest}")
        return dest

    headers = {"User-Agent": "Mozilla/5.0 (research bot)"}
    for url in pdf_urls:
        print(f"\n[2/4] Downloading: {url}")
        try:
            r = requests.get(url, headers=headers, timeout=30, allow_redirects=True)
            if r.status_code == 200 and b"%PDF" in r.content[:10]:
                dest.write_bytes(r.content)
                print(f"    Saved to: {dest}")
                return dest
            else:
                print(f"    Skipped (status {r.status_code} or not a PDF)")
        except Exception as e:
            print(f"    Failed: {e}")

    print("\n[2/4] Could not download any PDF.")
    return None

# ── Step 3: Extract text from PDF ────────────────────────────────────────────

def extract_text(pdf_path: Path) -> str:
    print(f"\n[3/4] Extracting text from PDF ...")
    if not pdf_path.exists():
        print(f"    Skipping: {pdf_path.name} not found.")
        return ""

    try:
        import pdfplumber
        with pdfplumber.open(pdf_path) as pdf:
            text = "\n".join(page.extract_text() or "" for page in pdf.pages)
        print(f"    Extracted {len(text)} characters.")
        return text
    except ImportError:
        pass
    except Exception as e:
        print(f"    pdfplumber failed ({e}), trying PyPDF2 ...")

    try:
        import PyPDF2
        with open(pdf_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            text = "\n".join(p.extract_text() or "" for p in reader.pages)
        print(f"    Extracted {len(text)} characters.")
        return text
    except ImportError:
        print("    ERROR: Install pdfplumber:  pip install pdfplumber")
    except Exception as e:
        print(f"    PyPDF2 failed ({e})")

    print("    Could not extract text — skipping.")
    return ""

# ── Step 4: Summarize & save .md + .txt ──────────────────────────────────────

def summarize_and_save(title: str, doi: str, text: str) -> Path:
    print(f"\n[4/4] Asking Claude to summarize the paper ...")

    excerpt = text[:12000] + ("\n...[truncated]" if len(text) > 12000 else "")

    prompt = (
        f"You are a research assistant. Below is the full text of a scientific paper.\n"
        f"Title: {title}\nDOI: {doi}\n\n"
        f"Paper text:\n{excerpt}\n\n"
        "Write a structured research summary in Markdown with these sections:\n"
        "## Title\n## Authors\n## Abstract\n## Keywords\n## Research Problem\n"
        "## Methodology\n## Key Findings\n## Contributions\n## Limitations\n## Conclusion\n"
        "Be concise and precise. Use bullet points where appropriate."
    )
    summary = call_claude(prompt, allow_web=False)
    log("STEP 4 - Summary", summary)

    OUTPUT_DIR.mkdir(exist_ok=True)
    stem = safe_doi(doi) + "_summary"

    md_path = OUTPUT_DIR / f"{stem}.md"
    md_path.write_text(summary, encoding="utf-8")
    print(f"    Markdown : {md_path}")
    return md_path

# ── Local PDF mode ───────────────────────────────────────────────────────────

def process_local_pdf(pdf_path: Path) -> Path | None:
    """Summarize a local PDF directly — no DOI lookup or download needed."""
    print(f"\n[local] Processing: {pdf_path.name}")
    log_session_start(pdf_path.stem)
    text = extract_text(pdf_path)
    if not text:
        print(f"  Skipped: could not extract text from {pdf_path.name}")
        return None
    title = pdf_path.stem
    return summarize_and_save(title, pdf_path.stem, text)

# ── Main ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    try:
        log_session_start(DOI)
        title, pdf_urls = get_pdf_links(DOI)
        pdf_path = download_pdf(pdf_urls, DOI)

        if pdf_path:
            text = extract_text(pdf_path)
            if text:
                md_out = summarize_and_save(title, DOI, text)
                print(f"\nDone! → {md_out}")
            else:
                print("\nCould not extract text from PDF.")
        else:
            print("\nNo PDF available — cannot generate summary.")

    except KeyboardInterrupt:
        print("\n[Interrupted by user.]")
