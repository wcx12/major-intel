# Repository Structure

This repository has three product lines:

- Function-call retrieval and agent orchestration.
- Gaokao volunteer-advising dialogue datasets.
- Crawlers, ingestion, and evidence-building pipelines.

The repository should keep those lines separated so public Git history stays
usable. Code, small seeds, tests, and documentation belong in Git. Raw crawls,
large database dumps, local cache files, PDFs, HTML snapshots, OCR packages,
logs, and generated dashboards should stay outside tracked source files.

## Target Layout

```text
major-intel/
  src/major_intel/
    function_calls/          # stable retrieval tools and function schemas
    agents/                  # rules entrypoint, DeepSeek agent, unified agent
    storage/                 # MySQL client, cache, traces, data-gap queues
    evaluation/              # smoke runners, oracles, boundary evaluators
    datasets/dialogue/       # dialogue cleaning and dataset build logic
    crawlers/                # reusable crawlers and extraction utilities
    ingestion/               # scripts that write crawled data into MySQL
    common/                  # shared config, text, JSON, and normalization helpers

  scripts/
    function_calls/          # thin CLI wrappers for function-call tools
    agents/                  # thin CLI wrappers for agent entrypoints
    datasets/                # thin CLI wrappers for dataset tasks
    crawlers/                # reusable CLI wrappers plus legacy batch scripts
    maintenance/             # one-off local maintenance commands

  datasets/
    dialogue/                # committed dialogue dataset snapshots and manifests
    eval_cases/              # committed function-call and agent evaluation cases
    samples/                 # small public sample data

  data/
    seeds/                   # small seed files needed by tests or local setup
    raw/                     # ignored local raw crawls
    interim/                 # ignored local intermediate data
    processed/               # ignored generated data products by default
    cache/                   # ignored local caches

  tests/
    function_calls/          # tests and manual READMEs per tool
    agents/                  # agent routing, trace, and function-call tests
    storage/                 # MySQL client, cache, and data-gap queue tests
    datasets/                # dialogue dataset cleaning and packaging tests
    crawlers/                # crawler and parser tests
    ingestion/               # database write and schema tests
    evaluation/              # smoke runner and evaluator tests

  docs/
    architecture/            # repository and system architecture
    function-calls/          # user-facing function-call behavior docs
    datasets/                # dataset sources, cleaning rules, and manifests
    crawlers/                # crawler operation notes and evidence policies
    operations/              # local setup, MySQL, smoke tests, and releases
    status/                  # current project status and issue logs
    archive/                 # historical docs kept for traceability

  reports/                  # generated reports; track only curated summaries
  outputs/                  # ignored generated outputs
  logs/                     # ignored logs
  tmp/                      # ignored local scratch files
```

## Rules

1. Keep stable importable code under `src/major_intel`.
2. Keep `scripts/*.py` as CLI wrappers or legacy compatibility shims.
3. Keep manual commands working while migrating internals.
4. Store public, small, reproducible datasets under `datasets/` or `data/seeds/`.
5. Do not commit local database dumps, raw crawl folders, generated dashboards,
   OCR packages, PDF caches, HTML caches, or `.env` files.
6. Every moved module keeps tests in the matching `tests/` subtree.

## Migration Policy

Migrate in small batches:

1. Function-call and agent core modules.
2. Dialogue dataset builders and cleaned dataset manifests.
3. Reusable crawler modules.
4. Legacy `curate_batch*.py` scripts into an archive-style crawler area.
5. Generated reports and research docs into curated documentation buckets.

Each batch must preserve existing CLI commands or explicitly document the new
command before the old command is removed.
