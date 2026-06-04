# Repository Reorganization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Separate function-call code, dialogue dataset work, and crawler work into clear repository areas while preserving existing manual test commands.

**Architecture:** Stable importable code moves into `src/major_intel`, and old `scripts/*.py` entrypoints remain as compatibility wrappers. Data and generated files are separated from source code through documented directories and `.gitignore` rules.

**Tech Stack:** Python, local MySQL CLI, unittest/pytest-compatible tests, PowerShell on Windows.

---

### Task 1: Document The Target Structure

**Files:**
- Create: `docs/architecture/repository-structure.md`
- Create: `docs/architecture/repository-reorganization-plan.md`

- [x] **Step 1: Add repository structure documentation**

Add the target layout and rules to `docs/architecture/repository-structure.md`.

- [x] **Step 2: Add this implementation plan**

Add this plan to `docs/architecture/repository-reorganization-plan.md`.

### Task 2: Create The Importable Package Skeleton

**Files:**
- Create: `src/major_intel/__init__.py`
- Create: `src/major_intel/function_calls/__init__.py`
- Create: `src/major_intel/agents/__init__.py`
- Create: `src/major_intel/storage/__init__.py`
- Create: `src/major_intel/evaluation/__init__.py`
- Create: `src/major_intel/common/__init__.py`
- Create: `scripts/_compat.py`

- [x] **Step 1: Create package directories**

Create empty package files so Python can import `major_intel.*` modules.

- [x] **Step 2: Add a compatibility helper**

Add `scripts/_compat.py` with a single `ensure_src_on_path()` function. The
function inserts repository `src/` into `sys.path` for direct script execution.

### Task 3: Move First-Batch Core Modules

**Files:**
- Move: `scripts/local_retrieval_mvp.py` -> `src/major_intel/storage/local_retrieval_mvp.py`
- Move: `scripts/agent_query_storage.py` -> `src/major_intel/storage/agent_query_storage.py`
- Move: `scripts/setup_entity_aliases.py` -> `src/major_intel/storage/setup_entity_aliases.py`
- Move: `scripts/retrieval_tools.py` -> `src/major_intel/function_calls/retrieval_tools.py`
- Move: `scripts/retrieval_function_registry.py` -> `src/major_intel/function_calls/registry.py`
- Move: `scripts/natural_language_entrypoint.py` -> `src/major_intel/agents/natural_language_entrypoint.py`
- Move: `scripts/deepseek_retrieval_agent.py` -> `src/major_intel/agents/deepseek_retrieval_agent.py`
- Move: `scripts/retrieval_agent_entrypoint.py` -> `src/major_intel/agents/retrieval_agent_entrypoint.py`
- Move: `scripts/run_retrieval_smoke_cases.py` -> `src/major_intel/evaluation/run_retrieval_smoke_cases.py`

- [x] **Step 1: Move files with Git-aware moves**

Use `git mv` for the nine stable core files so history stays traceable.

- [x] **Step 2: Update internal imports**

Replace imports from `scripts.*` inside moved modules with imports from
`major_intel.*`.

### Task 4: Preserve Existing CLI And Test Imports

**Files:**
- Recreate wrappers under the original `scripts/*.py` paths.

- [x] **Step 1: Add wrapper scripts**

Each wrapper imports `ensure_src_on_path()` and re-exports the moved module's
public names. CLI wrappers call the moved module's `main()` when executed.

- [x] **Step 2: Run focused compatibility tests**

Run:

```powershell
python scripts/retrieval_function_registry.py list-names
python scripts/retrieval_tools.py major_lookup --major "计科" --limit 2
python -m unittest tests.test_retrieval_function_registry tests.test_local_retrieval_mvp tests.test_agent_query_storage
```

Expected result: commands execute through the old paths while implementation
lives under `src/major_intel`.

### Task 5: Update Ignore Rules And Documentation Links

**Files:**
- Modify: `.gitignore`
- Modify: `README.md`
- Modify: selected `docs/status/*.md` links only when they point to moved implementation files.

- [x] **Step 1: Harden `.gitignore`**

Ignore local data products and scratch folders: `tmp/`, `outputs/`, `logs/`,
`data/cleaned/`, `data/interim/`, and generated report formats that should not
enter public Git history.

- [x] **Step 2: Update README architecture section**

Point readers to `src/major_intel` as implementation code and `scripts/` as
compatibility CLI entrypoints.

### Task 6: Verify First Batch

**Files:**
- No new files.

- [x] **Step 1: Run targeted unit tests**

Run:

```powershell
python -m unittest tests.test_retrieval_function_registry tests.test_retrieval_tools tests.test_natural_language_entrypoint tests.test_deepseek_retrieval_agent
```

- [x] **Step 2: Run smoke sample**

Run:

```powershell
python scripts/run_retrieval_smoke_cases.py --sample-per-tool 1 --report reports/retrieval_smoke_restructure_sample.json
```

- [x] **Step 3: Inspect Git status**

Run:

```powershell
git status --short
```

Only planned code, docs, and ignore changes should appear. Existing untracked
local data may still appear, but should not be staged.

### Task 7: Move Dialogue Dataset Code And Snapshot

**Files:**
- Move: `scripts/build_dialogue_assets.py` -> `src/major_intel/datasets/dialogue/build_dialogue_assets.py`
- Move: `clean/dialogue_claude_full/` -> `datasets/dialogue/claude_full/`
- Create: `src/major_intel/datasets/__init__.py`
- Create: `src/major_intel/datasets/dialogue/__init__.py`
- Create: `scripts/datasets/build_dialogue_assets.py`
- Recreate: `scripts/build_dialogue_assets.py` as a compatibility wrapper.
- Create: `datasets/dialogue/README.md`
- Modify: `README.md`, `docs/status/current-state.md`

- [x] **Step 1: Move stable dialogue builder code**

Move the importable dialogue asset builder into `src/major_intel/datasets/dialogue`.
Keep the old `scripts/build_dialogue_assets.py` command as a wrapper, and add a
new structured wrapper under `scripts/datasets/`.

- [x] **Step 2: Move committed dialogue snapshot**

Move the tracked formal snapshot from `clean/dialogue_claude_full/` into
`datasets/dialogue/claude_full/`. Leave untracked local experiments under
`clean/` untouched.

- [x] **Step 3: Update dataset documentation**

Document the new snapshot location, the builder location, and the generated
output policy. Generated rebuild output should default to ignored
`data/processed/dialogue/`, while committed snapshots live under
`datasets/dialogue/`.

- [x] **Step 4: Verify dialogue wrappers and tests**

Run:

```powershell
python scripts/build_dialogue_assets.py --limit 1 --output-dir data/processed/dialogue_smoke
python scripts/datasets/build_dialogue_assets.py --limit 1 --output-dir data/processed/dialogue_smoke_structured
python -m pytest tests/test_build_dialogue_assets.py -q
```

Expected result: old and structured CLI entrypoints both run, and the existing
unit tests pass without importing implementation code from `scripts/`.

### Task 8: Move Stable Rysxai Crawlers, Ingestion, And Reports

**Files:**
- Move: `scripts/rysxai_market_crawler.py` -> `src/major_intel/crawlers/rysxai_market_crawler.py`
- Move: `scripts/rysxai_civil_service_crawler.py` -> `src/major_intel/crawlers/rysxai_civil_service_crawler.py`
- Move: `scripts/rysxai_transfer_policy_crawler.py` -> `src/major_intel/crawlers/rysxai_transfer_policy_crawler.py`
- Move: `scripts/ingest_rysxai_data.py` -> `src/major_intel/ingestion/rysxai_data.py`
- Move: `scripts/rysxai_market_report.py` -> `src/major_intel/reporting/rysxai_market_report.py`
- Move: `scripts/build_rysxai_dashboards.py` -> `src/major_intel/reporting/rysxai_dashboards.py`
- Move: `scripts/build_rysxai_overview.py` -> `src/major_intel/reporting/rysxai_overview.py`
- Move: `scripts/build_rysxai_transfer_policy_dashboard.py` -> `src/major_intel/reporting/rysxai_transfer_policy_dashboard.py`
- Create package markers under `src/major_intel/crawlers/`, `src/major_intel/ingestion/`, and `src/major_intel/reporting/`.
- Recreate the original `scripts/*.py` files as compatibility wrappers.
- Create structured wrappers under `scripts/crawlers/`, `scripts/ingestion/`, and `scripts/reports/`.
- Modify docs that describe crawler implementation locations.

- [x] **Step 1: Move stable rysxai implementation modules**

Use `git mv` for the tracked stable rysxai modules. Do not move untracked
`curate_*.py`, raw seed files, generated reports, or local `clean/` experiments
in this batch.

- [x] **Step 2: Update internal imports**

Inside moved implementation modules, replace any internal imports from
`scripts.*` with `major_intel.*`. The known case is the market crawler importing
the markdown report writer.

- [x] **Step 3: Add compatibility wrappers**

Keep the original flat commands working, for example:

```powershell
python scripts/rysxai_market_crawler.py --help
python scripts/ingest_rysxai_data.py --help
python scripts/build_rysxai_transfer_policy_dashboard.py --help
```

Also expose structured wrappers, for example:

```powershell
python scripts/crawlers/rysxai_market_crawler.py --help
python scripts/ingestion/ingest_rysxai_data.py --help
python scripts/reports/build_rysxai_transfer_policy_dashboard.py --help
```

- [x] **Step 4: Verify crawler and ingestion tests**

Run:

```powershell
python -m pytest tests/test_rysxai_market_crawler.py tests/test_rysxai_civil_service_crawler.py tests/test_rysxai_transfer_policy_crawler.py tests/test_rysxai_market_report.py tests/test_rysxai_transfer_policy_dashboard.py tests/test_rysxai_data_ingestion.py -q
python -m unittest discover -s tests
```

Expected result: old imports through `scripts.*` keep working, structured
wrappers import successfully, and the full local suite still passes.

### Task 9: Inventory Local Workspace Noise

**Files:**
- Create: `docs/status/local-workspace-inventory-2026-06-04.md`
- Modify: `docs/architecture/repository-reorganization-plan.md`

- [x] **Step 1: Count untracked and ignored files**

Run read-only `git status`, `git ls-files --others --exclude-standard`, and
directory-size checks to understand local workspace noise without moving or
deleting files.

- [x] **Step 2: Classify local files by project use**

Classify untracked local files into local data products, generated reports,
dialogue experiment outputs, legacy curation scripts/tests, graduate outcome
pipeline candidates, and research docs.

- [x] **Step 3: Write the inventory report**

Write a concise report with counts, major patterns, risks, and the recommended
next execution order.

### Task 10: Graduate Outcome Pipeline Restructure

**Files:**
- Inspect: `scripts/graduate_outcome_crawler.py`
- Inspect: `scripts/rebuild_graduate_outcome_package.py`
- Inspect: `scripts/build_graduate_outcomes_dashboard.py`
- Inspect: `tests/test_graduate_outcome_crawler.py`
- Inspect: `tests/test_graduate_outcomes_dashboard.py`
- Inspect: `tests/test_graduate_outcomes_workbook_package.py`
- Potential create: `src/major_intel/crawlers/graduate_outcomes/`
- Potential create: `scripts/crawlers/graduate_outcomes/`

- [ ] **Step 1: Audit graduate outcome files**

Read the graduate outcome scripts and tests to decide which code is stable
enough to move into `src/major_intel` and which files should remain local or
legacy.

- [ ] **Step 2: Move stable graduate outcome modules**

Use `git mv` only for files selected after the audit. Keep old `scripts/*.py`
commands as compatibility wrappers.

- [ ] **Step 3: Verify graduate outcome tests**

Run:

```powershell
python -m pytest tests/test_graduate_outcome_crawler.py tests/test_graduate_outcomes_dashboard.py tests/test_graduate_outcomes_workbook_package.py -q
python -m unittest discover -s tests
```

Expected result: graduate outcome tests and the full suite pass, with no
changes to unrelated local data.
