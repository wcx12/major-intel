# Graduate Source Discovery Queue Report

Generated: 2026-06-14

## Summary

This dataset formalizes the source-discovery layer for graduate outcome
collection. It packages the 2024-2026 search task matrix, priority
recommendation-exemption queue, official-site URL candidates, search probe
results, probe seeds, crawl failures, and coverage summaries.

No person-level graduate outcome rows are included.

## Coverage

| Metric | Count |
|---|---:|
| Full discovery task rows | 26,532 |
| Priority recommendation task rows | 1,350 |
| Official-site discovery queue rows | 450 |
| School official-site URL rows | 430 |
| School-level summary rows | 2,948 |
| Search probe result rows | 370 |
| Probe seed rows | 13 |
| Failure rows | 150 |

## Task Matrix

| Field | Distribution |
|---|---|
| Years | 2024: 8,844; 2025: 8,844; 2026: 8,844 |
| Source types | recommendation exemption: 8,844; incoming recommendation: 8,844; postgraduate admission: 8,844 |
| Status | pending: 26,532 |

## Probe Quality

Only 12 of 370 search probe rows resolve to likely school, official, or CHSI
hosts. The rest are search-engine noise or broad public web results. These rows
are preserved for reproducibility and filtering, not as evidence sources.

## Failure Summary

The combined seed-failure table contains 150 rows. Most failures are HTTP 502
or network/SSL errors; a smaller number are HTTP 302, 403, 404, 412, or 422.
These failures help prioritize retry strategy and distinguish site access
issues from missing source evidence.
