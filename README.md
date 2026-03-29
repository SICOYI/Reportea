# Reportea

An automated, LLM-powered research pipeline that runs overnight — discovering papers, downloading PDFs, generating structured summaries, and producing a daily tech digest in newspaper style. Powered by the Claude CLI.

---

## How It Works

```
python scr/timer.py
        │
        │  [waits until 01:00 AM]
        │
01:00   ├── Build keywords library
        │     base_papers/*.pdf → KeywordExtractor (Claude) → all_kws
        │
        ├── Init: process base papers
        │     DOIExtractor → base DOIs
        │     → get_pdf_links → download_pdf → summarize_and_save → summaries/*.md
        │     → clear pdf_cache/
        │
        ├── Init: first discovery round
        │     CitationExtractor (base_papers/) → citation DOIs (validated + cached)
        │     → fetch keywords per DOI (Claude web) → keywords_list.csv
        │     → compare_csv_with_library → top-10 related DOIs
        │     → delete keywords_list.csv
        │
        └── Loop  [repeats until 04:00]
              process_dois → summaries/*.md
              CitationExtractor (pdf_cache/) → citation DOIs
              → keywords_list.csv → compare → next top-10 DOIs
              → clear pdf_cache/ + delete keywords_list.csv
              repeat ──────────────────────────────────────────┘
        │
04:00   └── summarizer.py → summaries/{YYYY-MM-DD}report.md
```

---

## Modules

| File | Role |
|---|---|
| `scr/timer.py` | Orchestrator — waits for 01:00, runs init + loop, calls summarizer at 04:00 |
| `scr/extractor.py` | Three extraction classes: `DOIExtractor`, `KeywordExtractor`, `CitationExtractor` |
| `scr/key_words_lib.py` | Builds keyword library; generates `keywords_list.csv`; compares against library to rank DOIs |
| `scr/calling_llm_reader.py` | DOI → PDF search → download → text extraction → Claude summary → `.md` |
| `scr/summarizer.py` | Reads all summary `.md` files, generates a newspaper-style daily tech digest |

---

## Extractor Classes (`scr/extractor.py`)

| Class | What it does |
|---|---|
| `DOIExtractor` | Scans `base_papers/*.pdf`, extracts each paper's own DOI from the first 3000 chars |
| `KeywordExtractor` | Calls Claude (no web) on the full paper text; returns normalized keyword set |
| `CitationExtractor` | Extracts cited DOIs from the references section, validates each via `doi.org`, caches to `doi_cache/` |

---

## Usage

### Run overnight (recommended)

```bash
python scr/timer.py
```

Starts watching the clock and triggers automatically at 01:00 AM. If already between 01:00–04:00, starts immediately.

### Run individual modules manually

```bash
# Build keyword library + generate CSV + rank related papers
python scr/key_words_lib.py

# Summarize a single paper by DOI  (edit DOI = "..." at top of file)
python scr/calling_llm_reader.py

# Generate today's tech digest from existing summaries
python scr/summarizer.py
```

---

## Setup

1. **Add your seed papers** — place PDF files into `base_papers/`. The pipeline extracts their DOIs and keywords to build the library, and uses their citation lists as the starting point for discovery.

2. **Install dependencies:**
   ```bash
   pip install requests pdfplumber
   ```

3. **Claude binary** — requires the Claude Code VS Code extension. If you see `FileNotFoundError`:
   ```bash
   ls ~/.vscode/extensions/ | grep anthropic
   # Update CLAUDE_BIN in each scr/*.py with the current version number
   ```

---

## Outputs

| Path | Content |
|---|---|
| `summaries/{safe_doi}_summary.md` | Structured research summary per paper (Title, Authors, Abstract, Keywords, Methodology, Findings, etc.) |
| `summaries/{YYYY-MM-DD}report.md` | Daily tech digest in newspaper format (≤500 words) |
| `doi_cache/*_cited_dois.json` | Validated citation DOIs per PDF — persists across runs to avoid re-validating |
| `keywords_list.csv` | Transient — written and deleted each cycle; `keywords (pipe-sep), doi` |
| `claude_responses.log` | Append-only log of every Claude interaction, separated by session |

### Daily Report Format

```
📰 Tech & Research Daily
### March 29, 2026

🔬 Today's Research Highlights
📌 Key Stories
💡 What This Means
🔭 On the Horizon
```

---

## File Structure

```
Reportea/
├── base_papers/              # Seed PDFs (input — add your papers here)
├── pdf_cache/                # Downloaded PDFs (auto-cleared each cycle)
├── doi_cache/                # Validated citation DOIs per PDF (persistent cache)
├── summaries/                # Generated .md summaries + daily report
├── scr/
│   ├── timer.py              # Orchestrator
│   ├── extractor.py          # DOIExtractor, KeywordExtractor, CitationExtractor
│   ├── key_words_lib.py      # Keyword library + CSV generation + comparison
│   ├── calling_llm_reader.py # DOI → PDF → summary
│   └── summarizer.py         # Daily tech digest generator
├── keywords_list.csv         # Transient (created/deleted each cycle)
└── claude_responses.log      # Full interaction log
```
