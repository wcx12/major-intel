from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

from scripts.local_retrieval_mvp import DbConfig, MysqlCliClient
from scripts.retrieval_tools import RetrievalTools


CASES = [
    ("exact", "杭州电子科技大学"),
    ("exact", "10336"),
    ("exact", "浙江大学"),
    ("exact", "10248"),
    ("exact", "南京航空航天大学"),
    ("exact", "华中科技大学"),
    ("exact", "电子科技大学"),
    ("exact", "西安电子科技大学"),
    ("exact", "北京邮电大学"),
    ("exact", "南京邮电大学"),
    ("exact", "重庆邮电大学"),
    ("alias_common", "杭电"),
    ("alias_common", "浙大"),
    ("alias_common", "西电"),
    ("alias_common", "北邮"),
    ("alias_common", "重邮"),
    ("alias_common", "南邮"),
    ("alias_common", "成电"),
    ("high_risk_short", "南航"),
    ("high_risk_short", "华科"),
    ("high_risk_short", "华大"),
    ("high_risk_short", "上交"),
    ("high_risk_short", "北工大"),
    ("high_risk_short", "北理"),
    ("high_risk_short", "南理"),
    ("high_risk_short", "哈工"),
    ("ambiguous", "中大"),
    ("ambiguous", "南大"),
    ("ambiguous", "交大"),
    ("ambiguous", "山大"),
    ("ambiguous", "河大"),
    ("ambiguous", "华师"),
    ("ambiguous", "华工"),
    ("ambiguous", "湖大"),
    ("broad", "科技大学"),
    ("broad", "师范大学"),
    ("broad", "医科大学"),
    ("broad", "电子"),
    ("broad", "交通"),
    ("broad", "大学"),
    ("contextual", "武汉华科"),
    ("contextual", "南京南航"),
    ("contextual", "上海上交"),
    ("contextual", "想问一下华科就业"),
    ("contextual", "孩子想去杭电"),
    ("contextual", "浙江的杭电"),
    ("negative", "火星第一职业技术学院"),
    ("negative", "不存在大学测试样本"),
    ("negative", "asdfghjkl"),
    ("negative", "大"),
]


def load_dotenv(path: Path) -> None:
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


def compact_result(group: str, text: str, result: dict[str, Any]) -> dict[str, Any]:
    data = result.get("data") or {}
    selected = data.get("selected_school") or {}
    candidates = data.get("candidates") or []
    fields = [
        "school_id",
        "code",
        "name",
        "province_name",
        "city_name",
        "type_name",
        "level_name",
        "alias_text",
        "alias_confidence",
    ]
    return {
        "group": group,
        "input": text,
        "status": result.get("status"),
        "normalized": result.get("normalized_slots") or {},
        "selected": {key: selected.get(key) for key in fields if selected.get(key) is not None},
        "candidate_count": len(candidates),
        "candidates": [
            {key: candidate.get(key) for key in fields if candidate.get(key) is not None}
            for candidate in candidates[:10]
        ],
        "warnings": result.get("warnings") or [],
        "needs_clarification": result.get("needs_clarification") or [],
    }


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    repo_root = Path(__file__).resolve().parents[1]
    load_dotenv(repo_root / ".env")
    tools = RetrievalTools(MysqlCliClient(DbConfig.from_env()))
    for group, text in CASES:
        try:
            result = tools.school_lookup(text, limit=10)
            row = compact_result(group, text, result)
        except Exception as exc:
            row = {
                "group": group,
                "input": text,
                "status": "exception",
                "error": f"{type(exc).__name__}: {exc}",
            }
        print(json.dumps(row, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
