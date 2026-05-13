# Changelog Monitoring Pipeline — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a replayable, staged pipeline that ingests SDK/API changelogs, classifies changes, analyzes codebase impact, generates migration guides, and produces a developer impact report.

**Architecture:** Modular stage-based pipeline with a state machine enforcing stage ordering. Each stage reads/writes disk artifacts. LLM calls go through a single Gemini client with taxonomy validation and audit logging.

**Tech Stack:** Python 3.10+, google-genai (Gemini 2.5 Flash), requests, BeautifulSoup4, python-dotenv

---

### Task 1: Project Scaffolding & Input Files

**Files:**
- Create: `requirements.txt`
- Create: `.env.example`
- Create: `changelog_sources.json`
- Create: `codebase_snippet.py`
- Create: `pipeline/__init__.py`
- Create: `pipeline/stages/__init__.py`
- Create: `pipeline/parsers/__init__.py`

- [ ] **Step 1:** Create `requirements.txt` with dependencies
- [ ] **Step 2:** Create `.env.example` with `GEMINI_API_KEY=your_key_here`
- [ ] **Step 3:** Create `changelog_sources.json` with the 3 sample sources
- [ ] **Step 4:** Create `codebase_snippet.py` with the sample Stripe code
- [ ] **Step 5:** Create empty `__init__.py` files for all packages

---

### Task 2: Taxonomy & State Machine

**Files:**
- Create: `pipeline/taxonomy.py`
- Create: `pipeline/state.py`

- [ ] **Step 1:** Create `pipeline/taxonomy.py` — enum classes for change types, risk levels, validation functions
- [ ] **Step 2:** Create `pipeline/state.py` — PipelineState enum, PipelineStateMachine class with transition enforcement

---

### Task 3: Configuration & LLM Client

**Files:**
- Create: `pipeline/config.py`
- Create: `pipeline/llm_client.py`

- [ ] **Step 1:** Create `pipeline/config.py` — load sources JSON, env vars, paths
- [ ] **Step 2:** Create `pipeline/llm_client.py` — Gemini wrapper with structured output, taxonomy validation, call logging to llm_calls.jsonl

---

### Task 4: Changelog Parsers

**Files:**
- Create: `pipeline/parsers/markdown_parser.py`
- Create: `pipeline/parsers/html_parser.py`

- [ ] **Step 1:** Create `pipeline/parsers/markdown_parser.py` — deterministic markdown changelog parsing (version headers, date extraction, entry splitting)
- [ ] **Step 2:** Create `pipeline/parsers/html_parser.py` — BeautifulSoup HTML parser with graceful failure

---

### Task 5: Pipeline Stages 1-3 (Fetch, Parse, Filter)

**Files:**
- Create: `pipeline/stages/s1_fetch.py`
- Create: `pipeline/stages/s2_parse.py`
- Create: `pipeline/stages/s3_filter.py`

- [ ] **Step 1:** Create `s1_fetch.py` — HTTP fetch all sources, save raw content, handle failures
- [ ] **Step 2:** Create `s2_parse.py` — route to markdown/html parser, generate entry_id, save to parsed_changelogs/
- [ ] **Step 3:** Create `s3_filter.py` — 90-day date filter, log discarded counts

---

### Task 6: Pipeline Stage 4 (Classification)

**Files:**
- Create: `pipeline/stages/s4_classify.py`

- [ ] **Step 1:** Create `s4_classify.py` — one LLM call per source, taxonomy validation, save to classified_changes.json

---

### Task 7: Pipeline Stages 5-8 (Impact, Migration, Validation)

**Files:**
- Create: `pipeline/stages/s5_select.py`
- Create: `pipeline/stages/s6_impact.py`
- Create: `pipeline/stages/s7_migration.py`
- Create: `pipeline/stages/s8_validate_code.py`

- [ ] **Step 1:** Create `s5_select.py` — filter Stripe high-risk entries
- [ ] **Step 2:** Create `s6_impact.py` — LLM call with high-risk entries + codebase snippet, per-function analysis
- [ ] **Step 3:** Create `s7_migration.py` — LLM call to generate before/after migration code
- [ ] **Step 4:** Create `s8_validate_code.py` — ast.parse validation of generated Python code

---

### Task 8: Pipeline Stages 9-10 (Report & Optional)

**Files:**
- Create: `pipeline/stages/s9_report.py`
- Create: `pipeline/stages/s10_optional.py`

- [ ] **Step 1:** Create `s9_report.py` — assemble impact_report.md with all required sections
- [ ] **Step 2:** Create `s10_optional.py` — security alerts, version pinning, diff simulation, TypeScript migration

---

### Task 9: Orchestrator & Validation

**Files:**
- Create: `run_pipeline.py`
- Create: `validate.py`
- Create: `Makefile`

- [ ] **Step 1:** Create `run_pipeline.py` — main entry point, stage orchestration, error handling
- [ ] **Step 2:** Create `validate.py` — 12-check validation suite
- [ ] **Step 3:** Create `Makefile` — run, validate, clean targets

---

### Task 10: End-to-End Test

- [ ] **Step 1:** Run `pip install -r requirements.txt`
- [ ] **Step 2:** Run `python run_pipeline.py` and verify all artifacts generated
- [ ] **Step 3:** Run `python validate.py` and verify all checks pass
