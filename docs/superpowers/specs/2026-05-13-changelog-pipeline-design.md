# Changelog Monitoring Pipeline — Design Spec

**Date:** 2026-05-13
**Status:** Approved

## Overview

A replayable, staged pipeline that monitors public SDK/API changelogs, classifies changes by type and breaking-change risk using LLM (Gemini 2.5 Flash free tier), evaluates high-risk changes against a codebase snippet, generates migration guides, and produces a developer impact report.

## Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Architecture | Modular stage-based (Approach B) | Maps 1:1 to spec stages, independently testable |
| LLM Provider | Google Gemini `gemini-2.5-flash` | Best free tier (15 RPM, 1M TPM) |
| Invocation | `python run_pipeline.py` + `Makefile` | Flexibility for evaluator |
| HTML Parsing | `requests` + `BeautifulSoup` (static) | Evaluator swaps fixtures; graceful failure |
| Dependencies | 4 packages (google-genai, requests, beautifulsoup4, python-dotenv) | Minimal footprint |

## Architecture

### Project Structure
```
changelog-pipeline/
├── run_pipeline.py          # Entry point
├── validate.py              # Validation command
├── Makefile                 # make run / validate / clean
├── requirements.txt
├── .env.example
├── changelog_sources.json   # Input
├── codebase_snippet.py      # Input
├── pipeline/
│   ├── __init__.py
│   ├── state.py             # State machine
│   ├── config.py            # Configuration
│   ├── taxonomy.py          # Controlled taxonomy
│   ├── llm_client.py        # Gemini wrapper + logging
│   ├── stages/
│   │   ├── s1_fetch.py through s10_optional.py
│   └── parsers/
│       ├── markdown_parser.py
│       └── html_parser.py
├── parsed_changelogs/       # Intermediate artifacts
└── llm_calls.jsonl          # Audit log
```

### Pipeline Stages
```
INIT → SOURCES_LOADED → CHANGELOGS_FETCHED → ENTRIES_PARSED →
RECENT_ENTRIES_FILTERED → CHANGES_CLASSIFIED → HIGH_RISK_STRIPE_CHANGES_SELECTED →
CODEBASE_IMPACT_ANALYSED → MIGRATION_GUIDES_GENERATED → MIGRATION_CODE_VALIDATED →
IMPACT_REPORT_WRITTEN → OPTIONAL_OUTPUTS_GENERATED → VALIDATION_COMPLETE → RESULTS_FINALISED
```

### LLM Calls (3-5 total)
1. Classify Stripe entries (Stage 4)
2. Classify OpenAI entries (Stage 4)
3. Classify Twilio entries (Stage 4)
4. Impact analysis — Stripe high-risk + codebase (Stage 6)
5. Migration guide generation (Stage 7)

### Error Handling
- Fetch failures → empty result with reason
- No 90-day entries → explicit empty result
- Invalid LLM taxonomy → flag, don't accept
- Invalid migration code → flag as not ready
- Missing API key → fail fast at INIT

### Validation (`python validate.py`)
12 checks covering artifact existence, JSON validity, taxonomy compliance, stage ordering, and migration code syntax.
