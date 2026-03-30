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
| `scr/calling_llm_reader.py` | DOI → PDF search → download → text extraction → Claude summary → `.md`; also accepts a local PDF path directly via `process_local_pdf()` |
| `scr/summarizer.py` | Reads all summary `.md` files, generates a newspaper-style daily tech digest; pushes it to your phone via ntfy.sh |
| `scr/email_sender.py` | ntfy.sh push notification client — sends the daily report to a subscribed topic |

---

## Extractor Classes (`scr/extractor.py`)

| Class | What it does |
|---|---|
| `DOIExtractor` | Scans `base_papers/*.pdf`, extracts each paper's own DOI from the first 3000 chars |
| `KeywordExtractor` | Calls Claude (no web) on the full paper text; returns normalized keyword set |
| `CitationExtractor` | Extracts cited DOIs from the references section, validates each via `doi.org`, caches to `doi_cache/` |

---

## Usage

### Overnight mode (scheduled)

```bash
python scr/timer.py
```

Waits until 01:00 AM, then runs until 04:00 AM and generates the daily digest.

### Immediate mode

```bash
python scr/timer.py --now        # start now, run for 1 hour
python scr/timer.py --now 2      # start now, run for 2 hours
```

Skips the 01:00 wait and runs for the specified number of hours, then generates the digest.

### Local mode

```bash
python scr/timer.py --local
```

Skips all DOI lookup and citation discovery. Reads every PDF already in `base_papers/` directly, generates a structured summary for each one, then produces the daily digest. Useful for quickly summarising a personal collection without running the full overnight pipeline.

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

3. **Phone notifications (optional)** — install the [ntfy app](https://ntfy.sh) on your phone, subscribe to your chosen topic, then set `TOPIC` in `scr/email_sender.py`. The daily report will be pushed automatically after each run.

4. **Claude binary** — requires the Claude Code VS Code extension. If you see `FileNotFoundError`:
   ```bash
   ls ~/.vscode/extensions/ | grep anthropic
   # Update CLAUDE_BIN in each scr/*.py with the current version number
   ```

---

## Outputs

| Path | Content |
|---|---|
| `summaries/{safe_doi}_summary.md` | Structured research summary per paper (Title, Authors, Abstract, Keywords, Methodology, Findings, etc.) |
| `summaries/{YYYY-MM-DD}report.md` | Daily tech digest in newspaper format (≤1500 words) |
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

## Known Issues

| # | Description | Impact |
|---|---|---|
| 1 | Papers without author-defined keywords cannot be processed — `KeywordExtractor` returns an empty set, causing the paper to be skipped in library building and CSV comparison | Base papers with no keyword section produce an empty library; citation papers with no keywords are excluded from ranking |
| 2 | Papers without a DOI cannot be processed — `DOIExtractor` relies on finding a DOI string in the PDF text; if none is present the paper yields no DOI and is skipped entirely | Base papers without a DOI contribute no entry point into the discovery pipeline |
| 3 | DOIs in reference lists that span multiple lines are truncated at the line break during PDF text extraction — the partial DOI fails `doi.org` validation and is discarded | Citation discovery rate can be very low for PDFs with wrapped reference formatting, reducing the number of related papers found per loop iteration |

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
│   ├── calling_llm_reader.py # DOI → PDF → summary; or local PDF → summary
│   ├── summarizer.py         # Daily tech digest generator
│   └── email_sender.py       # ntfy.sh push notification client
├── keywords_list.csv         # Transient (created/deleted each cycle)
├── claude_responses.log      # Full interaction log
└── .token_cache.json         # (not created — ntfy needs no auth)
```
