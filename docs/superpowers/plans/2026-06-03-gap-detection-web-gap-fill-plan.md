# Gap Detection And Web Gap Fill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a deterministic gap-detection and gap-filling workflow so local retrieval gaps are identified structurally, optionally filled through official web evidence, and never answered from rejected or third-party-only search snippets.

**Architecture:** Keep existing retrieval tools as the local fact layer. Upgrade `data_gap_detection` into the deterministic gap registry interface, add `web_gap_fill` as the multi-round gap-filling orchestrator, keep `web_evidence_fetch` as the single-round search/fetch/snippet extractor, and update the DeepSeek agent to call `web_gap_fill` before lower-level web tools.

**Tech Stack:** Python, pytest, SearXNG JSON API, existing `RetrievalTools` envelope, existing function-call registry, DeepSeek function-call agent.

---

## Current Problems

The current implementation can detect some gaps through `status`, `data_gaps`, and empty core lists, but the behavior is incomplete:

- `data_gap_detection` only covers a small set of question types and currently returns `ok` even when `missing_items` is non-empty.
- Several tools have implicit core fields but no shared registry that says which fields determine whether the tool actually found useful data.
- The agent fallback currently treats local `not_found` as a reason to call a web tool once, instead of planning multiple searches around a specific gap.
- `web_evidence_fetch` can fetch official page text, but it does not know what gap it is trying to fill.
- Third-party search results must never become facts unless verified through trusted sources.

## Target Flow

```text
Local retrieval tool result
-> Detect status/core-field/data_gaps signals
-> Build structured gap candidates
-> Call data_gap_detection for canonical gap definitions
-> Filter to resolvable_by_web=true gaps
-> web_gap_fill runs bounded multi-round search/fetch/evaluation
-> Return filled_items, accepted_evidence, unfilled_gaps
-> Agent answers only from filled_items and accepted_evidence
```

## Files

- Modify: `scripts/retrieval_tools.py`
  - Add core-field helpers.
  - Upgrade `data_gap_detection`.
  - Add `web_gap_fill`.
  - Add CLI parser and dispatcher entry for `web_gap_fill`.
- Modify: `scripts/retrieval_function_registry.py`
  - Register `web_gap_fill`.
  - Extend schema tests.
- Modify: `scripts/deepseek_retrieval_agent.py`
  - Prefer `web_gap_fill` over `web_evidence_fetch` and `web_evidence_search`.
  - Ensure final answer uses accepted evidence only.
- Create: `tests/test_gap_detection_registry.py`
  - Tests for core fields, available field inference, and structured gap items.
- Create: `tests/test_web_gap_fill.py`
  - Tests for bounded multi-round gap filling.
- Modify: `tests/test_retrieval_tools.py`
  - Update `data_gap_detection` status expectations.
- Modify: `tests/test_retrieval_function_registry.py`
  - Add `web_gap_fill` registry expectations.
- Modify: `tests/test_deepseek_retrieval_agent.py`
  - Add fallback priority test.
- Create: `tests/function_calls/web_gap_fill/README.md`
  - Function-call README for the new tool.
- Modify: `.env.example`
  - Add gap-fill limits if needed.

---

## Task 1: Add Core Result Field Registry

**Files:**
- Modify: `scripts/retrieval_tools.py`
- Create: `tests/test_gap_detection_registry.py`

- [ ] **Step 1: Write failing tests for core-field detection**

Add tests that prove empty core fields are detected independently from the tool status.

```python
from scripts.retrieval_tools import (
    _core_field_empty,
    _infer_available_fields,
)


def test_major_school_list_empty_schools_is_core_gap():
    result = {
        "tool_name": "major_school_list",
        "status": "ok",
        "data": {"major": {"special_name": "人工智能"}, "schools": []},
        "normalized_slots": {"major_name": "人工智能", "major_code": "080717T"},
        "data_gaps": [],
    }

    assert _core_field_empty("major_school_list", result) is True


def test_major_school_list_major_basic_is_available_when_major_exists():
    result = {
        "tool_name": "major_school_list",
        "status": "not_found",
        "data": {"major": {"special_name": "人工智能"}, "schools": []},
        "normalized_slots": {"major_name": "人工智能", "major_code": "080717T"},
    }

    fields = _infer_available_fields("major_school_list", result)

    assert "major_basic" in fields
    assert "major_code" in fields
    assert "major_school_relation" not in fields
```

- [ ] **Step 2: Run tests and verify failure**

Run:

```powershell
python -m pytest tests/test_gap_detection_registry.py -q
```

Expected failure:

```text
ImportError or AttributeError for _core_field_empty / _infer_available_fields
```

- [ ] **Step 3: Implement core-field registry and helpers**

Add helper definitions to `scripts/retrieval_tools.py`.

```python
TOOL_CORE_FIELDS = {
    "school_lookup": ["data.selected_school"],
    "major_lookup": ["data.selected_major"],
    "school_major_list": ["data.majors"],
    "major_school_list": ["data.schools"],
    "admission_history": ["data.records"],
    "plan_history": ["data.records", "data.plans"],
    "subject_requirement_lookup": ["data.requirements"],
    "policy_rule_lookup": ["data.rules"],
    "fee_and_campus_lookup": ["data.fee_items"],
    "web_evidence_fetch": ["data.evidence_pages"],
}


def _path_value(data: dict[str, Any], path: str) -> Any:
    current: Any = data
    for part in path.split("."):
        if not isinstance(current, dict):
            return None
        current = current.get(part)
    return current


def _has_non_empty_value(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, (list, tuple, set, dict)):
        return bool(value)
    if isinstance(value, str):
        return bool(value.strip())
    return True


def _core_field_empty(tool_name: str, result: dict[str, Any]) -> bool:
    paths = TOOL_CORE_FIELDS.get(tool_name)
    if not paths:
        return False
    return not any(_has_non_empty_value(_path_value(result, path)) for path in paths)
```

Add first-pass available-field inference:

```python
def _infer_available_fields(tool_name: str, result: dict[str, Any]) -> list[str]:
    fields: set[str] = set()
    data = result.get("data") if isinstance(result.get("data"), dict) else {}
    normalized = result.get("normalized_slots") if isinstance(result.get("normalized_slots"), dict) else {}

    if normalized.get("major_code"):
        fields.add("major_code")
    if normalized.get("major_name"):
        fields.add("major_basic")
    if normalized.get("school_name"):
        fields.add("school_basic")
    if normalized.get("province_filter") or normalized.get("province"):
        fields.add("province")
    if normalized.get("school_level_filter"):
        fields.add("school_level")

    if tool_name == "major_school_list":
        if _has_non_empty_value(data.get("major")):
            fields.add("major_basic")
        if _has_non_empty_value(data.get("schools")):
            fields.add("major_school_relation")
    if tool_name == "school_major_list":
        if _has_non_empty_value(data.get("school")):
            fields.add("school_basic")
        if _has_non_empty_value(data.get("majors")):
            fields.add("school_major_catalog")
    if tool_name == "admission_history" and _has_non_empty_value(data.get("records")):
        fields.add("admission_history")

    return sorted(fields)
```

- [ ] **Step 4: Run tests and verify pass**

Run:

```powershell
python -m pytest tests/test_gap_detection_registry.py -q
```

Expected:

```text
2 passed
```

---

## Task 2: Upgrade data_gap_detection To Structured Gap Items

**Files:**
- Modify: `scripts/retrieval_tools.py`
- Modify: `tests/test_retrieval_tools.py`
- Modify: `tests/function_calls/data_gap_detection/README.md`

- [ ] **Step 1: Write failing tests for partial status and gap_items**

Add or update tests in `tests/test_retrieval_tools.py`.

```python
def test_data_gap_detection_returns_partial_with_structured_gap_items():
    tools = RetrievalTools(FakeClient([]))

    result = tools.data_gap_detection(
        question_type="major_school_list",
        available_fields=["major_basic", "major_code", "province", "school_level"],
    )

    assert result["status"] == "partial"
    assert "missing_items" in result["data"]
    assert result["data"]["gap_items"][0]["gap_key"] == "major_school_relation"
    assert result["data"]["gap_items"][0]["resolvable_by_web"] is True
    assert "official" in result["data"]["gap_items"][0]["preferred_source_types"]
```

- [ ] **Step 2: Run tests and verify failure**

Run:

```powershell
python -m pytest tests/test_retrieval_tools.py::RetrievalToolsTests::test_data_gap_detection_returns_partial_with_structured_gap_items -q
```

Expected failure:

```text
AssertionError: 'ok' != 'partial' or missing gap_items
```

- [ ] **Step 3: Add gap registry**

Implement a deterministic registry in `scripts/retrieval_tools.py`.

```python
GAP_REGISTRY = {
    "major_school_relation": {
        "label": "专业开设院校关系",
        "question_types": ["major_school_list"],
        "required_fields": ["major_school_relation"],
        "resolvable_by_web": True,
        "preferred_source_types": ["chsi", "exam_authority", "official"],
        "evidence_requirements": [
            "school_name",
            "major_name_or_code",
            "undergraduate_level",
            "source_url",
            "evidence_snippet",
        ],
    },
    "school_major_catalog": {
        "label": "学校开设专业目录",
        "question_types": ["school_major_list"],
        "required_fields": ["school_major_catalog"],
        "resolvable_by_web": True,
        "preferred_source_types": ["official", "chsi"],
        "evidence_requirements": ["school_name", "major_name_or_code", "source_url", "evidence_snippet"],
    },
    "admission_history": {
        "label": "专业录取历史",
        "question_types": ["admission_history"],
        "required_fields": ["admission_history"],
        "resolvable_by_web": True,
        "preferred_source_types": ["exam_authority", "official"],
        "evidence_requirements": ["school_name", "major_name", "province", "year", "score_or_rank", "source_url"],
    },
    "official_admission_rule": {
        "label": "官方招生章程原文",
        "question_types": ["policy_rule_lookup"],
        "required_fields": ["official_admission_rule"],
        "resolvable_by_web": True,
        "preferred_source_types": ["official"],
        "evidence_requirements": ["school_name", "policy_text", "source_url", "evidence_snippet"],
    },
    "streaming_ratio": {
        "label": "真实分流比例",
        "question_types": ["major_streaming_policy_lookup"],
        "required_fields": ["streaming_ratio"],
        "resolvable_by_web": False,
        "non_resolvable_reason": "真实分流比例通常不是稳定公开数据，不能通过网页自动核验。",
        "preferred_source_types": [],
        "evidence_requirements": [],
    },
}
```

- [ ] **Step 4: Make data_gap_detection return structured partial**

Update `data_gap_detection`:

```python
def _gap_items_for_question_type(question_type: str, available_fields: set[str]) -> list[dict[str, Any]]:
    items = []
    for gap_key, definition in GAP_REGISTRY.items():
        if question_type not in definition.get("question_types", []):
            continue
        required_fields = set(definition.get("required_fields", []))
        if required_fields & available_fields:
            continue
        items.append({"gap_key": gap_key, **definition})
    return items
```

Status rule:

```python
status = "ok" if not gap_items else "partial"
```

Keep `data.missing_items`:

```python
missing_items = [item["label"] for item in gap_items]
```

- [ ] **Step 5: Update README**

Update `tests/function_calls/data_gap_detection/README.md` to say:

```text
known type + missing_items non-empty -> partial
known type + no missing_items -> ok
unknown type -> needs_clarification
```

- [ ] **Step 6: Run tests**

Run:

```powershell
python -m pytest tests/test_retrieval_tools.py -q
```

Expected:

```text
all retrieval tool tests pass
```

---

## Task 3: Detect Gaps From Tool Results

**Files:**
- Modify: `scripts/retrieval_tools.py`
- Modify: `tests/test_gap_detection_registry.py`

- [ ] **Step 1: Write failing tests**

```python
from scripts.retrieval_tools import _detect_tool_result_gaps


def test_detect_tool_result_gaps_from_not_found_major_school_list():
    result = {
        "tool_name": "major_school_list",
        "status": "not_found",
        "data": {"major": {"special_name": "人工智能"}, "schools": []},
        "normalized_slots": {
            "major_name": "人工智能",
            "major_code": "080717T",
            "province_filter": "上海",
            "school_level_filter": "本科",
        },
        "data_gaps": ["开设该专业的学校记录"],
    }

    gaps = _detect_tool_result_gaps("major_school_list", result)

    assert gaps[0]["gap_key"] == "major_school_relation"
    assert gaps[0]["trigger"] in {"status_not_found", "core_result_empty"}
    assert gaps[0]["resolvable_by_web"] is True
```

- [ ] **Step 2: Run test and verify failure**

Run:

```powershell
python -m pytest tests/test_gap_detection_registry.py::test_detect_tool_result_gaps_from_not_found_major_school_list -q
```

Expected:

```text
ImportError or AttributeError for _detect_tool_result_gaps
```

- [ ] **Step 3: Implement gap detection helper**

```python
TOOL_TO_QUESTION_TYPE = {
    "major_school_list": "major_school_list",
    "school_major_list": "school_major_list",
    "admission_history": "admission_history",
    "policy_rule_lookup": "policy_rule_lookup",
    "major_streaming_policy_lookup": "major_streaming_policy_lookup",
    "web_evidence_fetch": "web_evidence_fetch",
}


def _detect_tool_result_gaps(tool_name: str, result: dict[str, Any]) -> list[dict[str, Any]]:
    status = str(result.get("status") or "")
    if status in {"needs_clarification", "error", "skipped"}:
        return []

    core_empty = _core_field_empty(tool_name, result)
    has_data_gaps = bool(result.get("data_gaps"))
    if status not in {"not_found", "partial"} and not core_empty and not has_data_gaps:
        return []

    question_type = TOOL_TO_QUESTION_TYPE.get(tool_name, tool_name)
    available_fields = set(_infer_available_fields(tool_name, result))
    gap_items = _gap_items_for_question_type(question_type, available_fields)

    trigger = "status_not_found" if status == "not_found" else "partial_data_gap"
    if core_empty:
        trigger = "core_result_empty"

    normalized_slots = result.get("normalized_slots") if isinstance(result.get("normalized_slots"), dict) else {}
    return [
        {
            "source_tool": tool_name,
            "question_type": question_type,
            "trigger": trigger,
            "status": status,
            "raw_data_gaps": result.get("data_gaps") or [],
            "normalized_slots": normalized_slots,
            **item,
        }
        for item in gap_items
    ]
```

- [ ] **Step 4: Run tests**

Run:

```powershell
python -m pytest tests/test_gap_detection_registry.py -q
```

Expected:

```text
all gap detection registry tests pass
```

---

## Task 4: Register web_gap_fill Schema And CLI

**Files:**
- Modify: `scripts/retrieval_function_registry.py`
- Modify: `scripts/retrieval_tools.py`
- Modify: `tests/test_retrieval_function_registry.py`
- Create: `tests/function_calls/web_gap_fill/README.md`

- [ ] **Step 1: Write failing registry test**

Add `web_gap_fill` to `EXPECTED_FUNCTION_NAMES`.

Add fake method:

```python
def web_gap_fill(
    self,
    question,
    gap_type,
    normalized_slots=None,
    gap_keys=None,
    max_rounds=3,
    max_queries=8,
    max_pages=20,
    source_policy="official_only",
):
    self.calls.append(
        (
            "web_gap_fill",
            {
                "question": question,
                "gap_type": gap_type,
                "normalized_slots": normalized_slots,
                "gap_keys": gap_keys,
                "max_rounds": max_rounds,
                "max_queries": max_queries,
                "max_pages": max_pages,
                "source_policy": source_policy,
            },
        )
    )
    return tool_result("web_gap_fill", "not_found", {"question": question, "gap_type": gap_type})
```

- [ ] **Step 2: Run registry test and verify failure**

Run:

```powershell
python -m pytest tests/test_retrieval_function_registry.py -q
```

Expected failure:

```text
web_gap_fill missing from schemas
```

- [ ] **Step 3: Add schema**

In `scripts/retrieval_function_registry.py`, add:

```python
"web_gap_fill": _function_schema(
    "web_gap_fill",
    "围绕结构化数据缺口进行多轮网页补证。只把官方或高可信来源中通过正文证据验证的结果返回为 filled_items；第三方结果只能作为候选或诊断信息。",
    _object_schema(
        {
            "question": _string("用户原始问题。"),
            "gap_type": _string("缺口所属问题类型，例如 major_school_list。"),
            "normalized_slots": {
                "type": "object",
                "description": "上游工具解析出的结构化槽位。",
                "additionalProperties": True,
            },
            "gap_keys": _string_array("可选，需要补证的 gap_key 列表。"),
            "max_rounds": _integer("最多补证轮数。", minimum=1, maximum=5),
            "max_queries": _integer("最多尝试 query 数。", minimum=1, maximum=20),
            "max_pages": _integer("最多抓取页面数。", minimum=1, maximum=50),
            "source_policy": _string("来源策略：official_only、official_first 或 any。"),
        },
        ["question", "gap_type"],
    ),
),
```

- [ ] **Step 4: Add stub method**

In `RetrievalTools`, add a stub that validates inputs and returns not_found until Task 5 implements logic:

```python
def web_gap_fill(
    self,
    question: str,
    gap_type: str,
    normalized_slots: dict[str, Any] | None = None,
    gap_keys: list[str] | None = None,
    max_rounds: int = 3,
    max_queries: int = 8,
    max_pages: int = 20,
    source_policy: str = "official_only",
) -> dict[str, Any]:
    missing = _missing_slots({"question": question, "gap_type": gap_type})
    if missing:
        return _needs("web_gap_fill", {"question": question, "gap_type": gap_type}, missing)
    return tool_result(
        "web_gap_fill",
        "not_found",
        {
            "question": question,
            "gap_type": gap_type,
            "normalized_slots": normalized_slots or {},
            "gap_keys": gap_keys or [],
            "max_rounds": max_rounds,
            "max_queries": max_queries,
            "max_pages": max_pages,
            "source_policy": source_policy,
        },
        data={
            "filled_items": [],
            "accepted_evidence": [],
            "unfilled_gaps": [],
            "diagnostics": {"queries_tried": [], "pages_fetched": 0, "rejected_results": []},
        },
        data_gaps=["web_gap_fill_not_implemented"],
        source_tables=[],
    )
```

- [ ] **Step 5: Add CLI parser and README**

Add CLI arguments matching schema.

Create `tests/function_calls/web_gap_fill/README.md` with principles, input/output, status semantics, tests, and known risks.

- [ ] **Step 6: Run registry and directory tests**

Run:

```powershell
python -m pytest tests/test_retrieval_function_registry.py tests/test_function_call_readmes.py::test_function_call_test_directories_match_registered_tools -q
```

Expected:

```text
all selected tests pass
```

---

## Task 5: Implement Query Planner For major_school_relation

**Files:**
- Modify: `scripts/retrieval_tools.py`
- Create: `tests/test_web_gap_fill.py`

- [ ] **Step 1: Write failing tests for query planning**

```python
from scripts.retrieval_tools import _build_gap_fill_queries


def test_build_major_school_relation_queries_prioritize_official_sources():
    gap = {
        "gap_key": "major_school_relation",
        "normalized_slots": {
            "major_name": "人工智能",
            "major_code": "080717T",
            "province_filter": "上海",
            "school_level_filter": "本科",
        },
    }

    queries = _build_gap_fill_queries("major_school_list", [gap], candidate_schools=[])

    assert queries[0]["source_policy"] == "official_only"
    assert "site:gaokao.chsi.com.cn" in queries[0]["query"]
    assert "人工智能" in queries[0]["query"]
    assert "080717T" in queries[0]["query"]
```

- [ ] **Step 2: Run test and verify failure**

Run:

```powershell
python -m pytest tests/test_web_gap_fill.py::test_build_major_school_relation_queries_prioritize_official_sources -q
```

Expected:

```text
ImportError or AttributeError for _build_gap_fill_queries
```

- [ ] **Step 3: Implement query builder**

```python
def _build_gap_fill_queries(
    gap_type: str,
    gaps: list[dict[str, Any]],
    *,
    candidate_schools: list[str],
) -> list[dict[str, Any]]:
    if gap_type != "major_school_list":
        return []
    slots = gaps[0].get("normalized_slots") if gaps else {}
    major_name = _text(slots.get("major_name"))
    major_code = _text(slots.get("major_code"))
    province = _text(slots.get("province_filter"))
    level = _text(slots.get("school_level_filter") or "本科")
    base = " ".join(part for part in [major_name, major_code, level, province] if part)
    queries = [
        {"query": f"site:gaokao.chsi.com.cn {base}", "source_policy": "official_only"},
        {"query": f"site:chsi.com.cn {base} 普通本科", "source_policy": "official_only"},
        {"query": f"{province} 教育考试院 {major_name} {level} 招生计划", "source_policy": "official_only"},
    ]
    for school in candidate_schools[:10]:
        queries.append({"query": f"{school} {major_name} {level} 招生专业 官网", "source_policy": "official_only"})
    queries.append({"query": f"{province} 开设 {major_name} 专业 大学", "source_policy": "any"})
    return queries
```

- [ ] **Step 4: Run tests**

Run:

```powershell
python -m pytest tests/test_web_gap_fill.py -q
```

Expected:

```text
query planner tests pass
```

---

## Task 6: Implement Evidence Evaluator For major_school_relation

**Files:**
- Modify: `scripts/retrieval_tools.py`
- Modify: `tests/test_web_gap_fill.py`

- [ ] **Step 1: Write failing evaluator tests**

```python
from scripts.retrieval_tools import _evaluate_major_school_relation_evidence


def test_major_school_relation_evaluator_accepts_official_undergraduate_snippet():
    page = {
        "url": "https://zsb.sjtu.edu.cn/ai.html",
        "source_type": "official",
        "confidence": "high",
        "title": "上海交通大学本科招生专业",
        "evidence_snippets": [
            {"text": "上海交通大学本科招生专业目录包含人工智能专业。"}
        ],
    }
    slots = {"major_name": "人工智能", "major_code": "080717T", "school_level_filter": "本科"}

    evaluation = _evaluate_major_school_relation_evidence(page, slots)

    assert evaluation["accepted"] is True
    assert evaluation["filled_item"]["school_name"] == "上海交通大学"
    assert evaluation["filled_item"]["source_url"] == "https://zsb.sjtu.edu.cn/ai.html"
```

- [ ] **Step 2: Run test and verify failure**

Run:

```powershell
python -m pytest tests/test_web_gap_fill.py::test_major_school_relation_evaluator_accepts_official_undergraduate_snippet -q
```

Expected:

```text
ImportError or AttributeError for evaluator
```

- [ ] **Step 3: Implement evaluator**

```python
TRUSTED_WEB_SOURCE_TYPES = {"official", "exam_authority", "chsi"}
UNDERGRADUATE_MARKERS = {"本科", "普通本科", "本科招生", "招生专业", "专业目录"}


def _evaluate_major_school_relation_evidence(page: dict[str, Any], slots: dict[str, Any]) -> dict[str, Any]:
    if page.get("source_type") not in TRUSTED_WEB_SOURCE_TYPES:
        return {"accepted": False, "rejected_reason": "untrusted_source"}
    snippets = page.get("evidence_snippets") or []
    text = " ".join(str(item.get("text") or "") for item in snippets if isinstance(item, dict))
    major_name = _text(slots.get("major_name"))
    major_code = _text(slots.get("major_code"))
    if major_name not in text and (not major_code or major_code not in text):
        return {"accepted": False, "rejected_reason": "missing_major_name_or_code"}
    if not any(marker in text for marker in UNDERGRADUATE_MARKERS):
        return {"accepted": False, "rejected_reason": "missing_undergraduate_level"}
    school_name = _extract_school_name_from_page(page, text)
    if not school_name:
        return {"accepted": False, "rejected_reason": "missing_school_identity"}
    return {
        "accepted": True,
        "filled_item": {
            "gap_key": "major_school_relation",
            "school_name": school_name,
            "major_name": major_name,
            "major_code": major_code,
            "school_level": "本科",
            "source_type": page.get("source_type"),
            "source_url": page.get("url"),
            "evidence_snippet": snippets[0].get("text") if snippets else "",
            "confidence": page.get("confidence") or "medium",
        },
    }
```

Add minimal extractor:

```python
def _extract_school_name_from_page(page: dict[str, Any], text: str) -> str:
    title = _text(page.get("title"))
    combined = f"{title} {text}"
    for match in re.findall(r"[\u4e00-\u9fa5]{2,30}大学", combined):
        return match
    return ""
```

- [ ] **Step 4: Add rejection tests**

Add tests for:

```text
third_party rejected as untrusted_source
missing undergraduate marker rejected
missing major name/code rejected
```

- [ ] **Step 5: Run tests**

Run:

```powershell
python -m pytest tests/test_web_gap_fill.py -q
```

Expected:

```text
all evaluator tests pass
```

---

## Task 7: Implement web_gap_fill Loop

**Files:**
- Modify: `scripts/retrieval_tools.py`
- Modify: `tests/test_web_gap_fill.py`

- [ ] **Step 1: Write failing loop tests**

Use an injected fake `web_search_fetcher` that returns:

- Third-party search result in first query.
- Official page after candidate query.
- Official HTML containing an accepted snippet.

```python
def test_web_gap_fill_uses_third_party_only_as_candidate_then_verifies_official_page():
    calls = []

    def fetcher(url, timeout):
        calls.append(url)
        if "/search?" in url and "开设" in url:
            return json.dumps({"results": [{
                "title": "上海人工智能专业大学名单",
                "url": "https://example.com/ai-shanghai",
                "content": "上海交通大学开设人工智能专业。",
                "score": 1.0,
            }]}, ensure_ascii=False).encode("utf-8")
        if "/search?" in url and "上海交通大学" in url:
            return json.dumps({"results": [{
                "title": "上海交通大学本科招生专业",
                "url": "https://zsb.sjtu.edu.cn/ai.html",
                "content": "本科招生专业目录包含人工智能。",
                "score": 1.0,
            }]}, ensure_ascii=False).encode("utf-8")
        if url == "https://zsb.sjtu.edu.cn/ai.html":
            return "<html><body>上海交通大学本科招生专业目录包含人工智能专业。</body></html>".encode("utf-8")
        return json.dumps({"results": []}).encode("utf-8")

    tools = RetrievalTools(client=None, web_search_fetcher=fetcher)

    with patch.dict("os.environ", {"WEB_SEARCH_ENABLED": "true", "SEARXNG_BASE_URL": "http://127.0.0.1:8081"}, clear=True):
        result = tools.web_gap_fill(
            question="人工智能专业，上海有哪些本科院校开设？",
            gap_type="major_school_list",
            normalized_slots={"major_name": "人工智能", "major_code": "080717T", "province_filter": "上海", "school_level_filter": "本科"},
            max_rounds=3,
            max_queries=8,
            max_pages=10,
        )

    assert result["status"] == "ok"
    assert result["data"]["filled_items"][0]["school_name"] == "上海交通大学"
    assert result["data"]["diagnostics"]["rejected_results"]
```

- [ ] **Step 2: Run test and verify failure**

Run:

```powershell
python -m pytest tests/test_web_gap_fill.py::test_web_gap_fill_uses_third_party_only_as_candidate_then_verifies_official_page -q
```

Expected:

```text
status not_found from stub or missing loop
```

- [ ] **Step 3: Implement bounded loop**

Algorithm:

```python
def web_gap_fill(...):
    validate inputs and limits
    gap_items = _gap_items_for_question_type(gap_type, set(available_fields or []))
    active_gaps = filter gap_keys if provided
    if no resolvable gaps: return partial with unfilled_gaps
    queries = _build_gap_fill_queries(gap_type, active_gaps, candidate_schools=[])
    for query_plan in queries up to max_queries:
        call self.web_evidence_fetch(...)
        count pages
        evaluate accepted pages
        collect filled_items
        collect rejected_results
        extract candidate_schools from third-party rejected search results
        extend queries with official verification queries
        stop if max_pages reached or all required gaps filled
    return ok/partial/not_found
```

- [ ] **Step 4: Run web_gap_fill tests**

Run:

```powershell
python -m pytest tests/test_web_gap_fill.py -q
```

Expected:

```text
web_gap_fill tests pass
```

---

## Task 8: Update Agent Fallback Priority

**Files:**
- Modify: `scripts/deepseek_retrieval_agent.py`
- Modify: `tests/test_deepseek_retrieval_agent.py`

- [ ] **Step 1: Write failing test**

```python
def test_auto_runs_web_gap_fill_before_fetch_when_registered(self):
    # Fake model calls major_school_list.
    # Dispatcher returns not_found + data_gaps.
    # Agent should call web_gap_fill, not web_evidence_fetch.
```

Expected dispatcher calls:

```python
[
    ("major_school_list", {"major_text": "人工智能", "province_filter": "上海"}),
    ("web_gap_fill", {"question": "...", "gap_type": "major_school_list", ...}),
]
```

- [ ] **Step 2: Run test and verify failure**

Run:

```powershell
python -m pytest tests/test_deepseek_retrieval_agent.py::DeepSeekRetrievalAgentTests::test_auto_runs_web_gap_fill_before_fetch_when_registered -q
```

Expected:

```text
agent calls web_evidence_fetch or web_evidence_search instead
```

- [ ] **Step 3: Update fallback priority**

Add constants:

```python
WEB_GAP_FILL_TOOL = "web_gap_fill"
WEB_EVIDENCE_TOOLS = {WEB_GAP_FILL_TOOL, WEB_EVIDENCE_FETCH_TOOL, WEB_EVIDENCE_SEARCH_TOOL}
```

Update selection:

```python
def _web_fallback_tool_name(tools):
    if _tool_available(tools, WEB_GAP_FILL_TOOL):
        return WEB_GAP_FILL_TOOL
    if _tool_available(tools, WEB_EVIDENCE_FETCH_TOOL):
        return WEB_EVIDENCE_FETCH_TOOL
    if _tool_available(tools, WEB_EVIDENCE_SEARCH_TOOL):
        return WEB_EVIDENCE_SEARCH_TOOL
    return None
```

Build arguments for `web_gap_fill`:

```python
if tool_name == WEB_GAP_FILL_TOOL:
    arguments = {
        "question": user_text,
        "gap_type": _infer_gap_type_from_round_results(round_results),
        "normalized_slots": _merged_normalized_slots(round_results),
        "max_rounds": _web_gap_fill_max_rounds(),
        "max_queries": _web_gap_fill_max_queries(),
        "max_pages": _web_gap_fill_max_pages(),
        "source_policy": "official_only",
    }
```

- [ ] **Step 4: Run agent tests**

Run:

```powershell
python -m pytest tests/test_deepseek_retrieval_agent.py -q
```

Expected:

```text
all agent tests pass
```

---

## Task 9: Documentation And Real Smoke Tests

**Files:**
- Modify: `tests/function_calls/web_gap_fill/README.md`
- Modify: `tests/function_calls/data_gap_detection/README.md`

- [ ] **Step 1: Update web_gap_fill README**

Document:

```text
principle
input/output
status semantics
source policy
accepted vs rejected evidence
limits
test commands
known risks
```

- [ ] **Step 2: Run selected unit tests**

Run:

```powershell
python -m pytest tests/test_gap_detection_registry.py tests/test_web_gap_fill.py tests/test_retrieval_function_registry.py tests/test_deepseek_retrieval_agent.py tests/test_retrieval_tools.py -q
```

Expected:

```text
all selected tests pass
```

- [ ] **Step 3: Run real SearXNG smoke**

Run:

```powershell
$env:WEB_SEARCH_ENABLED='true'
$env:WEB_SEARCH_PROVIDER='searxng'
$env:SEARXNG_BASE_URL='http://127.0.0.1:8081'
python scripts\retrieval_tools.py web_gap_fill --question "人工智能专业，上海有哪些本科院校开设？" --gap-type major_school_list --normalized-slots-json "{\"major_name\":\"人工智能\",\"major_code\":\"080717T\",\"province_filter\":\"上海\",\"school_level_filter\":\"本科\"}" --max-rounds 3 --max-queries 8 --max-pages 20
```

Expected:

```text
status ok/partial/not_found
filled_items only when official evidence exists
third-party-only results remain in diagnostics
```

- [ ] **Step 4: Run real DeepSeek smoke**

Run:

```powershell
$env:WEB_SEARCH_ENABLED='true'
$env:WEB_SEARCH_PROVIDER='searxng'
$env:SEARXNG_BASE_URL='http://127.0.0.1:8081'
python scripts\deepseek_retrieval_agent.py "人工智能专业，上海有哪些本科院校开设？" --show-trace
```

Expected trace:

```text
major_school_list -> web_gap_fill
```

Expected answer:

```text
If official evidence is missing, do not list third-party candidates as confirmed schools.
If official evidence exists, cite URL and snippet.
```

---

## Risks And Guardrails

- Keep `web_evidence_fetch` as a lower-level tool. Do not put gap semantics into it.
- Do not let `web_gap_fill` expose rejected third-party results as answer-ready data.
- Do not web-search slot gaps. Missing `province`, `subject_type`, `year`, `rank_or_score`, or ambiguous entities should trigger clarification.
- Do not mark private or non-public data as web-resolvable.
- Add limits for rounds, queries, pages, and timeout before running real web calls.
- Keep the first implementation limited to `major_school_list`; expand after real smoke results are stable.

## Initial Scope

The first implementation should only fully support:

```text
major_school_list -> major_school_relation
```

It should define but not fully implement web filling for:

```text
school_major_list
admission_history
plan_history
subject_requirement_lookup
policy_rule_lookup
fee_and_campus_lookup
```

This keeps the first version testable and prevents broad, fragile behavior.

## Final Acceptance Criteria

- `data_gap_detection` returns `partial` when known question types still have missing fields.
- `data_gap_detection` returns structured `gap_items`.
- Core result fields exist for high-risk tools.
- Empty core fields produce structured gaps.
- `web_gap_fill` is registered as a function-call tool.
- `web_gap_fill` performs bounded multi-round filling for `major_school_list`.
- Third-party-only evidence never creates `filled_items`.
- The agent prefers `web_gap_fill` over `web_evidence_fetch` and `web_evidence_search`.
- Real agent trace shows local tool followed by `web_gap_fill`.
- Final answers cite accepted evidence URLs and snippets, or explicitly state that official verification failed.
