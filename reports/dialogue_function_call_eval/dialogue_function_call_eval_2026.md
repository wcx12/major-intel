# Dialogue Function-Call Eval Support Dataset Report

Generated: 2026-06-14

## Summary

The packaged dialogue support dataset adds a small, source-attributed public-ASR
question bank for testing question understanding and function-call routing in
major-intelligence workflows. It is a support corpus for evaluation and
retrieval behavior, not a factual evidence source for high-risk-major labels.

## Coverage

| Metric | Count |
|---|---:|
| ASR question candidates | 152 |
| Cleaned dialogue records | 152 |
| Full question-bank rows | 152 |
| Usable question-bank rows | 34 |
| Full function-call eval cases | 152 |
| Usable function-call eval cases | 34 |
| Mentor strategy records | 5 |
| Review-queue rows | 148 |
| Source inventory rows | 6 |

## Question Families

The largest intent groups are:

| Family | Questions | Usable |
|---|---:|---:|
| `rank_to_school_match` | 36 | 6 |
| `major_profile` | 34 | 9 |
| `school_major_profile` | 19 | 4 |
| `employment_summary` | 19 | 1 |
| `comparison_query` | 16 | 6 |
| `transfer_policy_lookup` | 11 | 2 |

## Routing Implications

- 143 of 152 eval cases expect clarification before a final answer.
- The most common expected tools are `major_lookup` (46), `rank_to_school_match`
  (45), `school_lookup` (41), `major_profile` (38), and `employment_summary`
  (26).
- Quality labels are intentionally retained across A-D. A/B rows form the
  direct regression subset; C/D rows remain useful for testing ASR noise,
  incomplete slots, and data-gap detection.

## Usage Limits

- Do not treat public-ASR-derived text as official admissions or employment
  evidence.
- Use official packages in this repository for claims about school, major,
  policy, score, employment, salary, or civil-service eligibility facts.
- Review raw ASR text before any user-facing product display.
