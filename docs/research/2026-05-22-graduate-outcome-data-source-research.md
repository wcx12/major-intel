# Graduate Outcome Data Source Research

Updated: 2026-05-22

## Objective

Build a usable all-school dataset for postgraduate outcome evidence, focused on:

- 保研资格/推荐名单: recommendation exemption lists published by recommending schools.
- 接收推免拟录取: recommendation-exemption admission lists published by receiving graduate schools.
- 考研/硕士拟录取: postgraduate admission lists published by graduate schools.

## Source Tiers

### A. Official Baseline School List

The current official school universe should come from the Ministry of Education's national higher education institution list:

- Source: https://www.moe.gov.cn/jyb_xxgk/s5743/s5744/202506/t20250627_1195683.html
- As of 2025-06-20, the Ministry page reports 3,167 higher education institutions: 2,919 ordinary HEIs, including 1,365 undergraduate schools and 1,554 higher vocational schools, plus 248 adult HEIs. The list excludes Hong Kong, Macau, and Taiwan.

The repository currently has `data/seeds/rysxai_universities.csv` with 2,948 schools. It is usable as an immediate operational baseline, but the final full crawl should reconcile it against the official Ministry list.

### B. CHSI / Yanzhao 推免 System

The national recommendation-exemption service system is the authoritative registry and disclosure platform:

- System page: https://yzst.chsi.com.cn/tm/wap/index
- 推免录取信息公开 page: https://yz.chsi.com.cn/tm/wap/lqmd/index

Important source constraints from the system page:

- Final recommendation-exemption lists, admission lists, and student-status registration are based on the system's filed records.
- Recommending schools and admission units still publish public notices on their own websites.
- Some录取信息公开 views require login, so this project should not attempt to bypass login or scrape private back-office data.

Therefore the crawler should use CHSI as authority context and prefer public school/graduate-school announcements as crawl targets.

### C. School Official Websites

Most usable data is in school-specific public pages and attachments:

- 教务处 / 本科生院 / 招生就业处: 推免资格、公示名单、名额分配.
- 研究生院 / 研究生招生网: 接收推免生拟录取名单、硕士研究生拟录取名单.
- 学院网站: school-level pages sometimes link only to college-level lists.

Attachment formats observed or expected:

- HTML tables
- `.xlsx` / `.xlsm`
- `.docx`
- `.pdf`
- legacy `.doc` files, which should be indexed and marked for review when not parseable.

## Recommended Pipeline

1. Use an all-school baseline to generate discovery tasks.
2. Resolve discovery tasks into official public URLs.
3. Crawl each URL within the same official domain, following relevant same-site pages and attachments.
4. Store raw pages/attachments, document evidence rows, extracted records, clean records, and summary tables separately.
5. Keep row-level source URLs and quality flags so downstream use can filter by confidence instead of trusting every extracted row equally.

## Current Implementation Status

Implemented:

- `scripts/graduate_outcome_crawler.py`
- `tests/test_graduate_outcome_crawler.py`
- `data/seeds/graduate_outcome_sources.sample.csv`
- `data/seeds/graduate_outcome_search_results.sample.csv`

Current generated local artifacts:

- `data/processed/graduate_outcomes/discovery_tasks_2024_2026.csv`
  - Built from 2,948 school rows.
  - Covers 2024, 2025, and 2026.
  - Contains 26,532 school-year-source discovery tasks.
- `data/processed/graduate_outcomes_chsi/chsi_schools_sample.csv`
  - Built from the first 2 CHSI graduate-school index pages.
  - Contains 40招生单位 rows.
- `data/processed/graduate_outcomes_chsi/chsi_seeds_10_l1_strict.csv`
  - Built from the first 10 CHSI schools, 1 bulletin-list page per school.
  - Contains 0 strict list seeds after filtering out policy/办法 bulletins.
- `data/processed/graduate_outcomes_sample/seeds.csv`
  - Built from a sample search-result CSV.
  - Demonstrates the discovery-result to crawler-seed handoff.
- `data/processed/graduate_outcomes_cli_smoke/records_clean.csv`
- `data/processed/graduate_outcomes_cli_smoke/school_year_summary.csv`

Current CHSI full-pass artifacts:

- `data/processed/graduate_outcomes_chsi/master_records_clean.csv`
  - Merged from 7 CHSI crawl chunks.
  - Contains 7,572 cleaned records from 7,610 extracted rows after deepening CHSI bulletin discovery to as many as 6 bulletin-list pages per school.
  - Covers 64招生单位, 152 school-year-document summary groups, and years 2008-2026.
  - Missing cleaned year count: 0.
- `data/processed/graduate_outcomes_chsi/master_records_public.csv`
  - Contains 7,572 de-identified rows for delivery/use.
  - Excludes raw `person_name` and `student_id`, while keeping masked identifiers and source URLs.
- `data/processed/graduate_outcomes_chsi/master_school_year_summary.csv`
  - Aggregated per school/year/document type/route.
- CHSI index coverage:
  - Probed CHSI graduate-school index pages 0-46.
  - Page 46 contains 19 units; page 47 contains 0 units.
  - Total indexed universe in this run is about 939招生单位.
- Seed discovery coverage:
  - Strict list-like bulletin seeds found in the first bulletin-list pass: 228.
  - Strict list-like bulletin seeds found after the 6-list deepening pass: 234.
  - Seed document crawl failures after discovery: 0.
  - Bulletin-discovery failures occurred during some school-list attempts, but discovered seed-document crawl failures remain 0.
- School-website recommendation-exemption discovery probe:
  - `data/processed/graduate_outcomes/official_site_discovery_queue_recommendation_exemption.csv` contains 450 undergraduate schools tagged with 保研.
  - `data/processed/graduate_outcomes/discovery_tasks_recommendation_exemption_recommended_2024_2026.csv` contains 1,350 school-year recommendation-exemption discovery tasks.
  - A 30-task Bing RSS probe returned 150 search rows but selected 0 usable seeds; observed results were mostly city/encyclopedia/tourism pages.
  - CHSI / 阳光高考 school-info and file-download samples returned HTTP 412 to the script, so this path needs browser-session/cookie handling, manual URL import, or another official source for school homepages.
- See `docs/research/graduate_outcome_chsi_crawl_summary_2026-05-22.md` for the short Chinese status material.

Current limits:

- Full URL discovery is implemented but public search providers are uneven:
  - Bing HTML returns a captcha page in this environment.
  - DuckDuckGo HTML returns an anti-bot challenge.
  - Bing RSS returns rows but gave poor Chinese-query relevance in tested samples; the recommendation-exemption probe produced 0 usable seeds from 150 result rows.
  - Therefore CHSI bulletin discovery and imported search-result CSVs are currently more reliable than direct public-search scraping.
- The all-school baseline is from the local rysxai seed, not yet reconciled with the 2025 Ministry list.
- `.xls` and legacy `.doc` parsing are not complete; those files are indexed for review unless a parser is added.
- PDF table extraction is basic and should be treated as lower confidence than HTML/Excel/docx tables.

## Commands

Generate all-school discovery tasks:

```powershell
python scripts/graduate_outcome_crawler.py `
  --build-discovery-tasks data/processed/graduate_outcomes/discovery_tasks_2024_2026.csv `
  --university-csv data/seeds/rysxai_universities.csv `
  --years 2026,2025,2024
```

Convert search results into crawler seeds:

```powershell
python scripts/graduate_outcome_crawler.py `
  --build-seed-csv data/processed/graduate_outcomes/seeds.csv `
  --discovery-tasks-csv data/processed/graduate_outcomes/discovery_tasks_2024_2026.csv `
  --search-results-csv data/processed/graduate_outcomes/search_results.csv
```

Collect search results directly when a provider works:

```powershell
python scripts/graduate_outcome_crawler.py `
  --collect-search-results data/processed/graduate_outcomes/search_results.csv `
  --discovery-tasks-csv data/processed/graduate_outcomes/discovery_tasks_2024_2026.csv `
  --search-start-index 0 `
  --search-max-tasks 100 `
  --results-per-query 5 `
  --search-provider bing-rss `
  --search-delay-seconds 1.5 `
  --resume
```

Collect CHSI招生单位 index in small chunks:

```powershell
python scripts/graduate_outcome_crawler.py `
  --collect-chsi-school-index data/processed/graduate_outcomes_chsi/chsi_schools_0_2.csv `
  --chsi-max-pages 2 `
  --chsi-page-size 20 `
  --chsi-delay-seconds 0.5
```

Collect CHSI bulletin seeds in small chunks:

```powershell
python scripts/graduate_outcome_crawler.py `
  --collect-chsi-bulletin-seeds data/processed/graduate_outcomes_chsi/chsi_seeds_0_10.csv `
  --chsi-school-csv data/processed/graduate_outcomes_chsi/chsi_schools_0_2.csv `
  --chsi-start-index 0 `
  --chsi-max-schools 10 `
  --chsi-max-bulletin-lists-per-school 1 `
  --chsi-delay-seconds 0 `
  --timeout-seconds 5
```

Run a chunked crawl:

```powershell
python scripts/graduate_outcome_crawler.py `
  --seed-csv data/processed/graduate_outcomes/seeds.csv `
  --raw-dir data/raw/graduate_outcomes `
  --processed-dir data/processed/graduate_outcomes/crawl `
  --logs-dir data/logs/graduate_outcomes `
  --start-index 0 `
  --max-seeds 100 `
  --max-pages 600 `
  --max-depth 1 `
  --delay-seconds 0.8 `
  --resume
```

Clean extracted records:

```powershell
python scripts/graduate_outcome_crawler.py `
  --clean-records `
  --records-jsonl data/processed/graduate_outcomes/crawl/records.jsonl `
  --clean-csv data/processed/graduate_outcomes/crawl/records_clean.csv `
  --summary-csv data/processed/graduate_outcomes/crawl/school_year_summary.csv
```

Merge multiple crawl chunks into one clean dataset:

```powershell
python scripts/graduate_outcome_crawler.py `
  --merge-records-jsonl `
  data/processed/graduate_outcomes_chsi/crawl_40_l1_v3/records.jsonl `
  data/processed/graduate_outcomes_chsi/crawl_p2_40_l1_v2/records.jsonl `
  data/processed/graduate_outcomes_chsi/crawl_p4_200_l1/records.jsonl `
  data/processed/graduate_outcomes_chsi/crawl_p14_200_l1_v2/records.jsonl `
  data/processed/graduate_outcomes_chsi/crawl_p24_200_l1/records.jsonl `
  data/processed/graduate_outcomes_chsi/crawl_p34_200_l1/records.jsonl `
  data/processed/graduate_outcomes_chsi/crawl_p44_59_l1/records.jsonl `
  --clean-csv data/processed/graduate_outcomes_chsi/master_records_clean.csv `
  --summary-csv data/processed/graduate_outcomes_chsi/master_school_year_summary.csv
```

Export a de-identified delivery CSV:

```powershell
python scripts/graduate_outcome_crawler.py `
  --export-public-clean `
  --clean-csv data/processed/graduate_outcomes_chsi/master_records_clean.csv `
  --public-csv data/processed/graduate_outcomes_chsi/master_records_public.csv
```

## Output Contract

The main usable files are:

- `documents.jsonl`: source-level evidence index.
- `records.jsonl`: extracted raw row records.
- `records.csv`: flat extraction table.
- `records_clean.csv`: deduplicated, masked, quality-scored analysis table.
- `records_public.csv` / `master_records_public.csv`: de-identified delivery table without raw `person_name` or `student_id`.
- `school_year_summary.csv`: per school/year/document type/route counts.
- `discovery_tasks_*.csv`: all-school search task queue for source discovery.

Every row should keep `source_url` and `title`; records without enough fields should be retained with `needs_review` / quality flags instead of silently discarded.
