# Function Call Tool Tests

This directory reserves one folder per retrieval function-call tool.

Concrete tests should live under the matching tool folder, for example:

```text
tests/function_calls/school_lookup/
tests/function_calls/major_lookup/
```

The initial per-tool README files are placeholders only. They are intentionally
not pytest test files, so creating the structure does not change test execution.

Every tool README should follow `tests/function_calls/README_TEMPLATE.md`.
The structure is enforced by `tests/test_function_call_readmes.py`.
