# Graduate Official Source Coverage Report

Generated: 2026-06-14

## Summary

This dataset formalizes the source-coverage layer behind the graduate outcome
support data. It captures official recommendation/admission source coverage,
remaining-source access decisions, official employment or teaching-quality
report sources, extracted metrics, and local artifact hashes.

Raw official source files are not embedded because many may contain public
person-level rows. The package therefore provides traceability without
redistributing unmasked original documents.

## Coverage

| Metric | Count |
|---|---:|
| School coverage rows | 430 |
| Schools with public official recommendation/admission records | 425 |
| Schools without public official recommendation/admission records | 5 |
| School-year source summary rows | 471 |
| Remaining-school recommendation attempts | 15 |
| Employment/report source rows | 74 |
| Employment/report metric rows | 326 |
| Local artifact metadata rows | 174 |

## Remaining-Source Attempt Decisions

| Decision | Count |
|---|---:|
| `ingested` | 10 |
| `no_ingest` | 5 |

Common blockers include web-visible but locally blocked downloads, JavaScript or
WAF challenges, no public row-level source, wrong document type, and login
requirements.

## Employment Report Extraction

| Extraction status | Count |
|---|---:|
| `metrics_extracted` | 28 |
| `no_ingest` | 40 |
| `source_only` | 6 |

The 326 extracted metric rows include official employment, destination
implementation, further-study, and related rates with source URL, scope, and
extraction-quality notes.

## Artifact Metadata

| Artifact state | Count |
|---|---:|
| Present locally | 73 |
| Referenced but not present | 101 |

For present artifacts the package records path, suffix, byte size, and SHA-256.
The raw files themselves are excluded from the zip package.
