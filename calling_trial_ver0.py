import subprocess
import requests
import re
from datetime import datetime
from pathlib import Path

CLAUDE_BIN = "/Users/mac/.vscode/extensions/anthropic.claude-code-2.1.81-darwin-x64/resources/native-binary/claude"
DOI = "10.1109/ACCESS.2023.3282453"
LOG_FILE = "claude_responses.log"
CACHE_DIR = Path("pdf_cache")
OUTPUT_DIR = Path("summaries")

# ── Helpers ──────────────────────────────────────────────────────────────────

def call_claude(prompt: str, allow_web: bool = True) -> str:
    args = [CLAUDE_BIN, "-p", prompt]
    if allow_web:
        args += ["--allowedTools", "WebFetch,WebSearch"]
    result = subprocess.run(args, capture_output=True, text=True)
    return result.stdout.strip()

def log(label: str, content: str):
    with open(LOG_FILE, "a") as f:
        f.write(f"[{datetime.now().isoformat()}] {label}\n")
        f.write(content + "\n")
        f.write("-" * 60 + "\n")

def extract_urls(text: str) -> list[str]:
    """Pull all http(s) URLs from Claude's response."""
    return re.findall(r'https?://[^\s\)\]\"\']+', text)

# ── Step 1: Find PDF links ────────────────────────────────────────────────────

def get_pdf_links(doi: str) -> tuple[str, list[str]]:
    print(f"\n[1/4] Searching for PDF links for DOI: {doi} ...")
    prompt = (
        f"Look up the paper with DOI: {doi}. "
        "Retrieve the paper title. "
        "Then search for freely available PDF versions on Semantic Scholar, "
        "Unpaywall (unpaywall.org), ResearchGate, and the publisher page. "
        "Return: 1) the paper title, 2) every direct PDF URL you find (full URLs ending in .pdf or PDF download links). "
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
    safe_doi = doi.replace("/", "_").replace(".", "-")
    dest = CACHE_DIR / f"{safe_doi}.pdf"

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

# ── Step 3: Extract text from PDF ─────────────────────────────────────────────

def extract_text(pdf_path: Path) -> str:
    print(f"\n[3/4] Extracting text from PDF ...")
    try:
        import pdfplumber
        with pdfplumber.open(pdf_path) as pdf:
            text = "\n".join(page.extract_text() or "" for page in pdf.pages)
        print(f"    Extracted {len(text)} characters.")
        return text
    except ImportError:
        print("    pdfplumber not found, trying PyPDF2 ...")
        try:
            import PyPDF2
            with open(pdf_path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                text = "\n".join(p.extract_text() or "" for p in reader.pages)
            print(f"    Extracted {len(text)} characters.")
            return text
        except ImportError:
            print("    ERROR: Install pdfplumber or PyPDF2:  pip install pdfplumber")
            return ""

# ── Step 4: Summarize & save Markdown ────────────────────────────────────────

def summarize_and_save(title: str, doi: str, text: str):
    print(f"\n[4/4] Asking Claude to summarize the paper ...")

    # Truncate if too long (keep first ~12000 chars to stay within prompt limits)
    excerpt = text[:12000] + ("\n...[truncated]" if len(text) > 12000 else "")

    prompt = (
        f"You are a research assistant. Below is the full text of a scientific paper.\n"
        f"Title: {title}\nDOI: {doi}\n\n"
        f"Paper text:\n{excerpt}\n\n"
        "Write a structured research summary in Markdown with these sections:\n"
        "## Title\n## Authors\n## Abstract\n## Research Problem\n"
        "## Methodology\n## Key Findings\n## Contributions\n## Limitations\n## Conclusion\n"
        "Be concise and precise. Use bullet points where appropriate."
    )
    summary = call_claude(prompt, allow_web=False)
    log("STEP 4 - Summary", summary)

    OUTPUT_DIR.mkdir(exist_ok=True)
    safe_doi = doi.replace("/", "_").replace(".", "-")
    out_path = OUTPUT_DIR / f"{safe_doi}_summary.md"
    out_path.write_text(summary, encoding="utf-8")
    print(f"    Markdown saved to: {out_path}")
    return out_path

# ── Main ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    try:
        title, pdf_urls = get_pdf_links(DOI)
        pdf_path = download_pdf(pdf_urls, DOI)

        if pdf_path:
            text = extract_text(pdf_path)
            if text:
                out = summarize_and_save(title, DOI, text)
                print(f"\nDone! Summary written to: {out}")
            else:
                print("\nCould not extract text from PDF.")
        else:
            print("\nNo PDF available — cannot generate summary.")

    except KeyboardInterrupt:
        print("\n[Interrupted by user.]")
