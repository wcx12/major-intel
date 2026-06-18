# Rysxai Market Crawler

## Purpose

The market crawler collects three source-level C datasets from rysxai public JSON APIs:

1. major-level macro employment observations
2. recruiting job posting samples
3. salary observations from rankings and job samples

These records are market observations only. They must not be presented as official school-major graduate outcomes.

Implementation lives in `src/major_intel/crawlers/rysxai_market_crawler.py`.
`scripts/rysxai_market_crawler.py` remains as the compatibility CLI wrapper,
and `scripts/crawlers/rysxai_market_crawler.py` is the structured CLI path.

For major-introduction-only crawling, use
`src/major_intel/crawlers/rysxai_major_intro_crawler.py`. It calls only
`profession/info/?id=...` and extracts:

- `major_detail`: 专业详情
- `major_course`: 专业课程
- `undergraduate_to_graduate`: 本研衔接
- `similar_majors`: 相似专业

Example:

```bash
python scripts/rysxai_major_intro_crawler.py \
  --refresh-profession-list data/seeds/rysxai_professions.full.csv \
  --all-professions \
  --resume \
  --sleep-seconds 0.1 \
  --concurrency 8 \
  --progress
```

It writes per-major snapshots to:

```text
data/processed/rysxai_major_intros/profession_{id}_major_intro_snapshot.json
```

and aggregate JSONL/CSV files to:

```text
data/processed/rysxai_major_intros/major_introductions_{run_id}.jsonl
data/processed/rysxai_major_intros/major_introductions_{run_id}.csv
```

## Inputs

Use rysxai profession ids, either directly:

```bash
python scripts/rysxai_market_crawler.py --profession-id 270
```

or from a CSV:

```bash
python scripts/rysxai_market_crawler.py --input-csv data/seeds/rysxai_professions.sample.csv
```

The CSV must contain either `rysxai_profession_id` or `profession_id`.

To refresh the full profession list:

```bash
python scripts/rysxai_market_crawler.py --refresh-profession-list data/seeds/rysxai_professions.full.csv
```

To run a safe smoke test against the first 20 discovered professions:

```bash
python scripts/rysxai_market_crawler.py \
  --input-csv data/seeds/rysxai_professions.full.csv \
  --resume \
  --max-count 20 \
  --sleep-seconds 2 \
  --progress \
  --reports-dir reports/rysxai
```

To run the full crawl in chunks:

```bash
python scripts/rysxai_market_crawler.py \
  --input-csv data/seeds/rysxai_professions.full.csv \
  --resume \
  --level 本科 \
  --sleep-seconds 2 \
  --max-consecutive-errors 20 \
  --progress \
  --reports-dir reports/rysxai
```

Then repeat with `--level 专科`.

## Source APIs

For each profession id, the crawler calls:

```text
https://api.rysxai.cn/api/ry_education/profession/info/?id={profession_id}
https://api.rysxai.cn/api/ry_education/profession/positions/?id={profession_id}
```

## Outputs

Raw API payloads are written to:

```text
data/raw/rysxai/
```

Normalized market snapshots are written to:

```text
data/processed/rysxai/profession_{id}_market_snapshot.json
```

Both output directories are ignored by git.

Run manifests and failures are written to:

```text
data/logs/rysxai/
```

Markdown reports are written to:

```text
reports/rysxai/
```

These generated outputs are also ignored by git.

## Normalized Snapshot Shape

Each snapshot uses `rysxai_market_snapshot/v1` and contains:

```json
{
  "schema_version": "rysxai_market_snapshot/v1",
  "source": {
    "name": "rysxai",
    "source_level": "C",
    "data_scope": "major_level_market_observation"
  },
  "profession": {},
  "macro_employment": {
    "industry_distribution": [],
    "region_distribution": [],
    "job_direction_distribution": []
  },
  "demand_ranking": [],
  "salary_ranking": [],
  "job_posting_samples": [],
  "salary_observations_by_city": {},
  "salary_observations_by_industry": {},
  "warnings": []
}
```

## Storage Guidance

Suggested downstream tables:

```text
major_employment_macro
job_posting_samples
salary_observations
source_documents
```

Keep official employment-quality-report data in separate A/B-level tables. Do not merge rysxai job samples into official school-major employment facts.

## Field Safety

The crawler intentionally keeps job/company fields and drops recruiter personal fields such as recruiter name and avatar. The retained job samples are enough for market analysis:

```text
job title, company name, city, district, industry, salary range, degree,
experience, skills, company tags, company scale, financing stage
```

## Crawl Safety

The crawler is intentionally conservative:

- single-process crawl
- configurable delay between professions
- retry with exponential backoff for transient failures
- no retry for blocking status codes such as 401 or 403
- optional resume mode to skip existing snapshots
- failure JSONL log instead of stopping the whole run on one missing/slow profession
- maximum consecutive failures guard

Do not use proxy rotation or captcha/login bypass for this source. If the site starts returning blocking responses, stop the run and reduce frequency or seek permission.
