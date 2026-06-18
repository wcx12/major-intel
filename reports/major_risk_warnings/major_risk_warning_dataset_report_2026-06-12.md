# Major Employment Warning Dataset

- Built at: 2026-06-14T13:30:37+08:00
- Records: 570
- Sources: 458 ({'fetched': 455, 'blocked_client_challenge': 1, 'cached_after_fetch_error': 2})
- Red records: 218
- Yellow records: 122
- Green records: 230
- Metric records: 1314
- Official policy warning records: 9151

## Files

- `data/processed/major_risk_warnings/major_risk_warning_records.csv`
- `data/processed/major_risk_warnings/major_risk_warning_records.jsonl`
- `data/processed/major_risk_warnings/major_risk_warning_metrics.csv`
- `data/processed/major_risk_warnings/major_risk_warning_official_policy_warnings.csv`
- `data/processed/major_risk_warnings/major_risk_warning_major_summary.csv`
- `data/processed/major_risk_warnings/major_risk_warning_year_summary.csv`
- `data/processed/major_risk_warnings/major_risk_warning_sources.csv`
- `data/processed/major_risk_warnings/major_risk_warning_coverage.csv`
- `data/raw/major_risk_warnings/`

## Latest Explicit Red Lists

- 本科 2025: 公共事业管理、法学、绘画、美术学、音乐表演
- 高职高专 2025: 小学教育、小学英语教育、小学语文教育、法律事务、美术教育

## Highest Red-Flag Frequency

| level | major | red_count | red_years | latest_risk |
|---|---:|---:|---|---|
| 本科 | 法学 | 16 | 2009;2010;2011;2012;2013;2014;2015;2017;2018;2019;2020;2021;2022;2023;2024;2025 | red |
| 高职高专 | 小学语文教育 | 16 | 2010;2011;2012;2013;2014;2015;2016;2017;2018;2019;2020;2021;2022;2023;2024;2025 | red |
| 高职高专 | 法律事务 | 16 | 2010;2011;2012;2013;2014;2015;2016;2017;2018;2019;2020;2021;2022;2023;2024;2025 | red |
| 本科 | 音乐表演 | 11 | 2009;2015;2016;2017;2018;2019;2020;2021;2022;2024;2025 | red |
| 高职高专 | 小学教育 | 10 | 2015;2017;2018;2019;2020;2021;2022;2023;2024;2025 | red |
| 本科 | 应用心理学 | 8 | 2015;2016;2019;2020;2021;2022;2023;2024 | yellow |
| 本科 | 绘画 | 8 | 2018;2019;2020;2021;2022;2023;2024;2025 | red |
| 本科 | 美术学 | 8 | 2013;2014;2015;2016;2017;2018;2024;2025 | red |
| 本科 | 生物技术 | 7 | 2010;2011;2012;2013;2014;2016;2017 | yellow |
| 本科 | 生物工程 | 7 | 2010;2011;2012;2013;2014;2015;2017 | yellow |
| 高职高专 | 小学英语教育 | 6 | 2019;2021;2022;2023;2024;2025 | red |
| 本科 | 英语 | 5 | 2009;2010;2011;2012;2013 | yellow |
| 本科 | 动画 | 5 | 2010;2011;2012;2013;2014 | yellow |
| 本科 | 体育教育 | 5 | 2010;2011;2012;2013;2014 | yellow |
| 高职高专 | 国际金融 | 5 | 2010;2011;2012;2013;2015 | red |
| 高职高专 | 计算机应用技术 | 5 | 2010;2011;2012;2013;2014 | yellow |
| 本科 | 生物科学与工程 | 5 | 2010;2011;2012;2013;2014 | red |
| 高职高专 | 电子商务 | 5 | 2010;2011;2012;2013;2014 | red |
| 本科 | 历史学 | 4 | 2017;2018;2019;2021 | red |
| 本科 | 化学 | 4 | 2016;2018;2019;2020 | red |

## Caveats

- This is a public-source dataset, not an official Ministry of Education prohibition list.
- `confidence=medium` rows are derived from public consecutive-year counts or secondary text excerpts and should be prioritized for manual review.
- 2026 public data found in this pass contains undergraduate and high-vocational green-list records; no high-confidence 2026 red/yellow list was found during this crawl.
- Historical high-vocational specialty names changed across catalog revisions; `reported_major_name` keeps source wording and `standard_major_name` gives a best-effort current-name alias.

## Failed Sources

- `scribd_2024_undergrad_text`: fetched challenge page; no usable article text
- `hnu_2025_major_catalog_pdf`: fetch_error_reused_cached_raw: ReadTimeout(ReadTimeoutError("HTTPSConnectionPool(host='xxgk.hnu.edu.cn', port=443): Read timed out. (read timeout=40)"))
- `nenu_2024_teaching_quality_report_pdf`: fetch_error_reused_cached_raw: ChunkedEncodingError(ProtocolError('Connection broken: IncompleteRead(42790 bytes read, 5221176 more expected)', IncompleteRead(42790 bytes read, 5221176 more expected)))
