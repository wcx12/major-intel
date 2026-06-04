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
