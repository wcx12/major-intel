"""Build a static dashboard for crawled rysxai transfer-major policies."""

from __future__ import annotations

import argparse
import html as html_lib
import json
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_JSONL_PATH = ROOT / "data" / "raw" / "rysxai_transfer_policies.jsonl"
DEFAULT_OUTPUT_PATH = ROOT / "reports" / "rysxai" / "transfer_policy_dashboard.html"

MOJIBAKE_MARKERS = frozenset(
    "澶嶆棪涓婃捣鏈娴欐睙鍖椾含鏉窞缁煎悎鍏姙鏁欒偛"
    "杞笓涓氭斂绛栫敵璇锋潯浠跺噯鍏ヨ姹傝€冩牳"
)


def repair_mojibake(value: str) -> str:
    """Repair UTF-8 text that was decoded as GB18030 by the upstream payload."""
    if not value or value.isascii():
        return value
    try:
        repaired = value.encode("gb18030").decode("utf-8")
    except UnicodeError:
        return value
    if repaired == value:
        return value
    if _private_use_count(value) or _mojibake_marker_count(value) >= 2:
        return repaired
    return value


def load_jsonl_records(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSONL at {path}:{line_number}") from exc
    return records


def build_dashboard_model(records: list[dict[str, Any]]) -> dict[str, Any]:
    rows = []
    endpoint_counts: Counter[str] = Counter()
    level_counts: Counter[str] = Counter()
    province_counts: Counter[str] = Counter()
    length_buckets: Counter[str] = Counter()
    policy_char_values = []
    latest_fetched_at = ""

    for index, record in enumerate(records):
        school = record.get("school") or {}
        source = record.get("source") or {}
        availability = record.get("availability") or {}
        policy = record.get("transfer_policy") or {}

        source_url = str(source.get("source_url") or "")
        endpoint_key, endpoint_label = endpoint_from_url(source_url)
        has_policy = bool(availability.get("has_transfer_policy"))
        has_faculty_policy = bool(availability.get("has_faculty_policy"))
        faculty_count = to_int(availability.get("faculty_policy_count"))
        policy_chars = to_int(availability.get("change_profession_chars"))
        total_section_chars = sum(
            to_int(availability.get(key))
            for key in (
                "change_profession_chars",
                "application_condition_chars",
                "admission_requirement_chars",
                "assessment_chars",
            )
        )
        province = display_text(school.get("province"), "未标注")
        level = display_text(school.get("level"), "未标注")
        fetched_at = str(record.get("fetched_at") or "")
        latest_fetched_at = max(latest_fetched_at, fetched_at)

        endpoint_counts[endpoint_label] += 1
        level_counts[level] += 1
        province_counts[province] += 1
        length_buckets[length_bucket(policy_chars)] += 1
        if has_policy:
            policy_char_values.append(policy_chars)

        tags = [repair_mojibake(str(tag)) for tag in school.get("tags") or []]
        rows.append(
            {
                "index": index,
                "schoolId": to_int(school.get("id")),
                "schoolName": display_text(school.get("name"), "未命名学校"),
                "province": province,
                "city": display_text(school.get("city"), ""),
                "schoolType": display_text(school.get("type"), ""),
                "property": display_text(school.get("property"), ""),
                "level": level,
                "department": display_text(school.get("department"), ""),
                "tags": tags,
                "endpointKey": endpoint_key,
                "endpoint": endpoint_label,
                "sourceUrl": source_url,
                "hasPolicy": has_policy,
                "hasFacultyPolicy": has_faculty_policy,
                "facultyCount": faculty_count,
                "policyChars": policy_chars,
                "totalSectionChars": total_section_chars,
                "lengthBucket": length_bucket(policy_chars),
                "isNewVersion": bool(policy.get("is_new_version")),
                "excerpt": policy_excerpt(policy),
            }
        )

    total = len(rows)
    schools_with_policy = sum(1 for row in rows if row["hasPolicy"])
    schools_with_faculty = sum(1 for row in rows if row["hasFacultyPolicy"])
    empty_policy_schools = total - schools_with_policy

    return {
        "summary": {
            "totalSchools": total,
            "schoolsWithPolicy": schools_with_policy,
            "emptyPolicySchools": empty_policy_schools,
            "schoolsWithFacultyPolicy": schools_with_faculty,
            "coverageRate": percentage(schools_with_policy, total),
            "facultyPolicyRate": percentage(schools_with_faculty, total),
            "latestFetchedAt": latest_fetched_at,
            "maxPolicyChars": max(policy_char_values, default=0),
            "avgPolicyChars": round(sum(policy_char_values) / len(policy_char_values))
            if policy_char_values
            else 0,
        },
        "charts": {
            "endpointCounts": chart_items(endpoint_counts),
            "levelCounts": chart_items(level_counts),
            "provinceCounts": chart_items(province_counts, limit=18),
            "lengthBuckets": chart_items(
                length_buckets,
                order=["空白", "1-999字", "1000-4999字", "5000-14999字", "15000字以上"],
            ),
        },
        "filters": {
            "provinces": sorted(province_counts),
            "levels": sorted(level_counts),
            "endpoints": ["新接口", "旧接口", "未知接口"],
        },
        "records": rows,
        "emptySchools": [row for row in rows if not row["hasPolicy"]],
        "topFacultySchools": sorted(
            [row for row in rows if row["hasFacultyPolicy"]],
            key=lambda row: (row["facultyCount"], row["policyChars"]),
            reverse=True,
        )[:24],
    }


def render_dashboard(model: dict[str, Any]) -> str:
    summary = model["summary"]
    payload_json = json.dumps(model, ensure_ascii=False, separators=(",", ":")).replace(
        "</", "<\\/"
    )
    subtitle = (
        "数据源：data/raw/rysxai_transfer_policies.jsonl；"
        f"最近抓取：{summary['latestFetchedAt'] or '未标注'}；页面可离线打开。"
    )
    metrics = "\n".join(
        [
            metric("学校总数", fmt_int(summary["totalSchools"]), "唯一 school_id"),
            metric(
                "有政策文本",
                fmt_int(summary["schoolsWithPolicy"]),
                f"覆盖率 {summary['coverageRate']}%",
            ),
            metric("接口空白", fmt_int(summary["emptyPolicySchools"]), "需官网复核"),
            metric(
                "院系细则",
                fmt_int(summary["schoolsWithFacultyPolicy"]),
                f"结构化率 {summary['facultyPolicyRate']}%",
            ),
            metric("最长政策", fmt_int(summary["maxPolicyChars"]), "change_profession 字符"),
            metric("平均长度", fmt_int(summary["avgPolicyChars"]), "仅统计有文本学校"),
        ]
    )

    return f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>转专业政策可视化</title>
<style>
:root {{
  --bg:#f6f8fb; --panel:#fff; --text:#182230; --muted:#667085; --line:#d9e1ea;
  --blue:#0969da; --green:#087443; --amber:#b54708; --red:#b42318;
  --ink:#344054; --soft:#eef4fb; --shadow:0 8px 22px rgba(16,24,40,.06);
}}
* {{ box-sizing:border-box; }}
html, body {{ margin:0; background:var(--bg); color:var(--text); font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","Microsoft YaHei",sans-serif; }}
a {{ color:var(--blue); text-decoration:none; }}
.topbar {{ position:sticky; top:0; z-index:5; background:rgba(255,255,255,.96); border-bottom:1px solid var(--line); }}
.top-inner, .page {{ max-width:1440px; margin:0 auto; padding:16px 24px; }}
.top-inner {{ display:grid; grid-template-columns:1fr auto; gap:16px; align-items:end; }}
h1 {{ margin:0; font-size:26px; line-height:1.2; letter-spacing:0; }}
h2 {{ margin:0; font-size:18px; letter-spacing:0; }}
.sub, .note {{ color:var(--muted); font-size:13px; line-height:1.55; }}
.sub {{ margin-top:6px; }}
.nav {{ display:flex; gap:8px; flex-wrap:wrap; justify-content:flex-end; }}
.nav a {{ height:34px; display:inline-flex; align-items:center; padding:0 10px; border:1px solid var(--line); border-radius:6px; background:white; font-size:13px; color:var(--ink); }}
.nav a.active {{ background:#e8f2ff; border-color:#b8d8ff; color:#0756ad; }}
.page {{ display:grid; gap:16px; padding-top:22px; padding-bottom:42px; }}
.metrics {{ display:grid; grid-template-columns:repeat(6,minmax(128px,1fr)); gap:12px; }}
.metric, .panel {{ background:var(--panel); border:1px solid var(--line); border-radius:8px; box-shadow:var(--shadow); }}
.metric {{ padding:14px; min-height:84px; }}
.metric-label {{ color:var(--muted); font-size:12px; margin-bottom:8px; }}
.metric-value {{ font-size:25px; font-weight:760; line-height:1; }}
.metric-foot {{ margin-top:8px; color:var(--muted); font-size:12px; white-space:normal; }}
.grid-2 {{ display:grid; grid-template-columns:1fr 1fr; gap:16px; align-items:start; }}
.grid-3 {{ display:grid; grid-template-columns:1fr 1fr 1fr; gap:16px; align-items:start; }}
.panel-head {{ padding:14px 16px; display:flex; justify-content:space-between; gap:12px; align-items:flex-start; border-bottom:1px solid var(--line); }}
.panel-body {{ padding:14px 16px; }}
.bar-list {{ display:grid; gap:9px; }}
.bar {{ display:grid; grid-template-columns:minmax(92px,152px) 1fr auto; gap:10px; align-items:center; font-size:13px; }}
.bar-name {{ overflow:hidden; white-space:nowrap; text-overflow:ellipsis; color:var(--ink); }}
.track {{ height:9px; border-radius:999px; overflow:hidden; background:#e8eef5; }}
.fill {{ height:100%; border-radius:999px; background:var(--blue); min-width:2px; }}
.fill.green {{ background:var(--green); }}
.fill.amber {{ background:var(--amber); }}
.count {{ color:var(--muted); font-variant-numeric:tabular-nums; }}
.controls {{ display:flex; flex-wrap:wrap; gap:10px; }}
input, select {{ height:38px; border:1px solid var(--line); border-radius:6px; padding:0 11px; background:white; color:var(--text); font-size:14px; }}
input {{ min-width:310px; }}
select {{ min-width:145px; }}
.table-wrap {{ max-height:720px; overflow:auto; }}
table {{ width:100%; border-collapse:collapse; font-size:13px; }}
th {{ position:sticky; top:0; z-index:1; background:#eef3f8; text-align:left; color:#3d4a5c; font-size:12px; padding:10px 12px; border-bottom:1px solid var(--line); white-space:nowrap; }}
td {{ padding:10px 12px; border-bottom:1px solid #edf1f5; vertical-align:top; }}
tbody tr:hover td {{ background:#f3f9ff; }}
.school-cell {{ min-width:190px; }}
.school-name {{ font-weight:720; color:#101828; }}
.school-meta {{ color:var(--muted); font-size:12px; margin-top:3px; }}
.badge {{ display:inline-flex; align-items:center; min-height:22px; padding:2px 8px; border-radius:999px; background:#e7f0fa; color:#155c9e; font-size:12px; white-space:nowrap; }}
.badge.good {{ background:#e2f4ea; color:var(--green); }}
.badge.warn {{ background:#fff2dc; color:var(--amber); }}
.badge.bad {{ background:#fde8e7; color:var(--red); }}
.tags {{ display:flex; flex-wrap:wrap; gap:4px; max-width:180px; }}
.tag {{ display:inline-flex; align-items:center; min-height:20px; padding:1px 6px; border-radius:4px; background:#eef2f6; color:#475467; font-size:12px; }}
.excerpt {{ max-width:360px; color:#475467; line-height:1.45; display:-webkit-box; -webkit-line-clamp:2; -webkit-box-orient:vertical; overflow:hidden; }}
.list {{ display:grid; gap:9px; }}
.list-row {{ display:grid; grid-template-columns:1fr auto; gap:12px; padding:8px 0; border-bottom:1px solid #edf1f5; font-size:13px; }}
.list-row:last-child {{ border-bottom:0; }}
.muted {{ color:var(--muted); }}
.data-row {{ display:grid; grid-template-columns:190px 1fr; gap:12px; padding:10px 0; border-bottom:1px solid #edf1f5; font-size:14px; }}
.data-row:last-child {{ border-bottom:0; }}
.code {{ font-family:ui-monospace,SFMono-Regular,Consolas,monospace; color:#344054; }}
.empty {{ padding:24px; text-align:center; color:var(--muted); }}
@media (max-width:1120px) {{
  .metrics {{ grid-template-columns:repeat(3,1fr); }}
  .grid-2, .grid-3, .top-inner {{ grid-template-columns:1fr; }}
  .nav {{ justify-content:flex-start; }}
}}
@media (max-width:720px) {{
  .top-inner, .page {{ padding-left:14px; padding-right:14px; }}
  .metrics {{ grid-template-columns:1fr 1fr; }}
  input, select {{ width:100%; min-width:0; }}
  .bar {{ grid-template-columns:90px 1fr 44px; }}
  th.hide-sm, td.hide-sm {{ display:none; }}
  .data-row {{ grid-template-columns:1fr; }}
}}
</style>
</head>
<body>
<header class="topbar">
  <div class="top-inner">
    <div>
      <h1>转专业政策可视化</h1>
      <div class="sub">{html_lib.escape(subtitle)}</div>
    </div>
    <nav class="nav">
      <a href="index.html">总入口</a>
      <a class="active" href="transfer_policy_dashboard.html">转专业政策</a>
      <a href="undergraduate_market_overview.html">本科就业</a>
      <a href="vocational_market_overview.html">专科就业</a>
      <a href="civil_service_2026_overview.html">考公岗位</a>
    </nav>
  </div>
</header>
<main class="page">
  <section class="metrics">{metrics}</section>

  <section class="grid-3">
    <article class="panel">
      <div class="panel-head"><h2>接口命中</h2><div class="note">新接口优先，404 后回落旧接口</div></div>
      <div class="panel-body"><div id="endpointBars" class="bar-list"></div></div>
    </article>
    <article class="panel">
      <div class="panel-head"><h2>学校层次</h2><div class="note">按学校列表字段统计</div></div>
      <div class="panel-body"><div id="levelBars" class="bar-list"></div></div>
    </article>
    <article class="panel">
      <div class="panel-head"><h2>政策长度</h2><div class="note">按 change_profession 字段分桶</div></div>
      <div class="panel-body"><div id="lengthBars" class="bar-list"></div></div>
    </article>
  </section>

  <section class="grid-2">
    <article class="panel">
      <div class="panel-head"><h2>省份覆盖</h2><div class="note">展示学校数量最多的地区</div></div>
      <div class="panel-body"><div id="provinceBars" class="bar-list"></div></div>
    </article>
    <article class="panel">
      <div class="panel-head"><h2>院系细则较多的学校</h2><div class="note">新接口常见结构化字段</div></div>
      <div class="panel-body"><div id="topFacultyList" class="list"></div></div>
    </article>
  </section>

  <section class="panel">
    <div class="panel-head">
      <div>
        <h2>学校明细筛选</h2>
        <div class="note" id="resultCount">正在载入</div>
      </div>
      <div class="controls">
        <input id="searchInput" placeholder="搜索学校、省份、城市、标签" />
        <select id="provinceSelect"><option value="">全部省份</option></select>
        <select id="levelSelect"><option value="">全部层次</option></select>
        <select id="endpointSelect"><option value="">全部接口</option></select>
        <select id="policySelect">
          <option value="">全部政策状态</option>
          <option value="has">有政策</option>
          <option value="empty">接口空白</option>
          <option value="faculty">有院系细则</option>
        </select>
      </div>
    </div>
    <div class="table-wrap">
      <table>
        <thead>
          <tr>
            <th>学校</th>
            <th>地区</th>
            <th>层次</th>
            <th>接口</th>
            <th>状态</th>
            <th class="hide-sm">院系细则</th>
            <th class="hide-sm">政策长度</th>
            <th class="hide-sm">摘要</th>
            <th>来源</th>
          </tr>
        </thead>
        <tbody id="tableBody"></tbody>
      </table>
    </div>
  </section>

  <section class="grid-2">
    <article class="panel">
      <div class="panel-head"><h2>接口空白学校</h2><div class="note">不是“无政策”，只是 rysxai 未暴露文本</div></div>
      <div class="panel-body"><div id="emptyList" class="list"></div></div>
    </article>
    <article class="panel">
      <div class="panel-head"><h2>使用注意</h2><div class="note">适合作为线索库，不适合作为最终政策依据</div></div>
      <div class="panel-body">
        <div class="data-row"><strong>来源等级</strong><div>rysxai 是第三方整理数据，当前按 C 级线索处理；高风险使用前要回到学校官网、教务处或招生章程复核。</div></div>
        <div class="data-row"><strong>字段含义</strong><div>新接口通常有 <span class="code">change_profession_by_faculty</span> 等结构化院系细则；旧接口多为合并后的政策文本。</div></div>
        <div class="data-row"><strong>空白解释</strong><div>“接口空白”只说明抓取时没有返回转专业字段，不等于学校没有转专业政策。</div></div>
        <div class="data-row"><strong>全文位置</strong><div><span class="code">data/raw/rysxai_transfer_policies.jsonl</span> 存全文；<span class="code">data/processed/rysxai_transfer_policies.csv</span> 方便表格查看。</div></div>
        <div class="data-row"><strong>显示修复</strong><div>本页对常见 UTF-8/GB18030 错码做了可视化层修复；原始抓取文件保持未改动，便于追溯。</div></div>
      </div>
    </article>
  </section>
</main>
<script id="payload" type="application/json">{payload_json}</script>
<script>
const payload = JSON.parse(document.getElementById("payload").textContent);
const rows = payload.records;
const state = {{
  q: "",
  province: "",
  level: "",
  endpoint: "",
  policy: ""
}};

function fmtInt(value) {{
  return Number(value || 0).toLocaleString("zh-CN");
}}

function escapeHtml(value) {{
  return String(value ?? "").replace(/[&<>"']/g, ch => ({{
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#39;"
  }}[ch]));
}}

function optionList(id, values) {{
  const select = document.getElementById(id);
  values.forEach(value => {{
    const option = document.createElement("option");
    option.value = value;
    option.textContent = value;
    select.appendChild(option);
  }});
}}

function renderBars(id, items, colorClass = "") {{
  const el = document.getElementById(id);
  const max = Math.max(...items.map(item => item.value), 1);
  el.innerHTML = items.map(item => {{
    const width = Math.max(2, Math.round(item.value / max * 100));
    return `<div class="bar">
      <div class="bar-name" title="${{escapeHtml(item.label)}}">${{escapeHtml(item.label)}}</div>
      <div class="track"><div class="fill ${{colorClass}}" style="width:${{width}}%"></div></div>
      <div class="count">${{fmtInt(item.value)}}</div>
    </div>`;
  }}).join("");
}}

function badge(row) {{
  if (!row.hasPolicy) return '<span class="badge bad">接口空白</span>';
  if (row.hasFacultyPolicy) return '<span class="badge good">有院系细则</span>';
  return '<span class="badge">有政策</span>';
}}

function tableRow(row) {{
  const tags = row.tags.slice(0, 4).map(tag => `<span class="tag">${{escapeHtml(tag)}}</span>`).join("");
  const source = row.sourceUrl
    ? `<a href="${{escapeHtml(row.sourceUrl)}}" target="_blank" rel="noreferrer">API</a>`
    : '<span class="muted">无</span>';
  return `<tr>
    <td class="school-cell"><div class="school-name">${{escapeHtml(row.schoolName)}}</div><div class="school-meta">ID ${{row.schoolId || ""}}</div></td>
    <td>${{escapeHtml(row.province)}}<div class="school-meta">${{escapeHtml(row.city)}}</div></td>
    <td>${{escapeHtml(row.level)}}<div class="school-meta">${{escapeHtml(row.property || row.schoolType)}}</div></td>
    <td><span class="badge ${{row.endpoint === "新接口" ? "good" : "warn"}}">${{escapeHtml(row.endpoint)}}</span></td>
    <td>${{badge(row)}}<div class="tags">${{tags}}</div></td>
    <td class="hide-sm">${{fmtInt(row.facultyCount)}}</td>
    <td class="hide-sm">${{fmtInt(row.policyChars)}}<div class="school-meta">${{escapeHtml(row.lengthBucket)}}</div></td>
    <td class="hide-sm"><div class="excerpt">${{escapeHtml(row.excerpt || "暂无摘要")}}</div></td>
    <td>${{source}}</td>
  </tr>`;
}}

function applyFilters() {{
  const q = state.q.trim().toLowerCase();
  const filtered = rows.filter(row => {{
    if (state.province && row.province !== state.province) return false;
    if (state.level && row.level !== state.level) return false;
    if (state.endpoint && row.endpoint !== state.endpoint) return false;
    if (state.policy === "has" && !row.hasPolicy) return false;
    if (state.policy === "empty" && row.hasPolicy) return false;
    if (state.policy === "faculty" && !row.hasFacultyPolicy) return false;
    if (!q) return true;
    return [
      row.schoolName, row.province, row.city, row.level, row.endpoint,
      row.department, row.tags.join(" ")
    ].join(" ").toLowerCase().includes(q);
  }});
  const limit = 700;
  document.getElementById("tableBody").innerHTML = filtered.slice(0, limit).map(tableRow).join("");
  document.getElementById("resultCount").textContent =
    `命中 ${{fmtInt(filtered.length)}} 所学校${{filtered.length > limit ? `，表格先显示前 ${{limit}} 条` : ""}}`;
}}

function renderCompactList(id, list, emptyText, formatter) {{
  const el = document.getElementById(id);
  if (!list.length) {{
    el.innerHTML = `<div class="empty">${{escapeHtml(emptyText)}}</div>`;
    return;
  }}
  el.innerHTML = list.map(formatter).join("");
}}

optionList("provinceSelect", payload.filters.provinces);
optionList("levelSelect", payload.filters.levels);
optionList("endpointSelect", payload.filters.endpoints);

renderBars("endpointBars", payload.charts.endpointCounts, "green");
renderBars("levelBars", payload.charts.levelCounts, "");
renderBars("lengthBars", payload.charts.lengthBuckets, "amber");
renderBars("provinceBars", payload.charts.provinceCounts, "");

renderCompactList("topFacultyList", payload.topFacultySchools, "暂无院系细则数据", row =>
  `<div class="list-row"><div><strong>${{escapeHtml(row.schoolName)}}</strong><div class="muted">${{escapeHtml(row.province)}} · ${{escapeHtml(row.level)}} · ${{escapeHtml(row.endpoint)}}</div></div><div class="count">${{fmtInt(row.facultyCount)}} 个</div></div>`
);

renderCompactList("emptyList", payload.emptySchools, "没有接口空白学校", row =>
  `<div class="list-row"><div><strong>${{escapeHtml(row.schoolName)}}</strong><div class="muted">${{escapeHtml(row.province)}} · ${{escapeHtml(row.level)}} · ${{escapeHtml(row.endpoint)}}</div></div><div class="count">ID ${{row.schoolId}}</div></div>`
);

document.getElementById("searchInput").addEventListener("input", event => {{
  state.q = event.target.value;
  applyFilters();
}});
document.getElementById("provinceSelect").addEventListener("change", event => {{
  state.province = event.target.value;
  applyFilters();
}});
document.getElementById("levelSelect").addEventListener("change", event => {{
  state.level = event.target.value;
  applyFilters();
}});
document.getElementById("endpointSelect").addEventListener("change", event => {{
  state.endpoint = event.target.value;
  applyFilters();
}});
document.getElementById("policySelect").addEventListener("change", event => {{
  state.policy = event.target.value;
  applyFilters();
}});
applyFilters();
</script>
</body>
</html>
"""


def write_dashboard(jsonl_path: Path, output_path: Path) -> Path:
    records = load_jsonl_records(jsonl_path)
    model = build_dashboard_model(records)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(render_dashboard(model), encoding="utf-8")
    return output_path


def display_text(value: Any, default: str = "") -> str:
    text = repair_mojibake(str(value or "").strip())
    return text or default


def endpoint_from_url(source_url: str) -> tuple[str, str]:
    if "/docs/new/" in source_url:
        return "new", "新接口"
    if "/docs/" in source_url:
        return "legacy", "旧接口"
    return "unknown", "未知接口"


def policy_excerpt(policy: dict[str, Any], max_chars: int = 180) -> str:
    for key in (
        "change_profession",
        "change_profession_application_condition",
        "change_profession_admission_requirement",
        "change_profession_assessment",
    ):
        text = repair_mojibake(str(policy.get(key) or ""))
        text = " ".join(text.replace("\n", " ").split())
        if text:
            return text[:max_chars] + ("..." if len(text) > max_chars else "")
    return ""


def length_bucket(chars: int) -> str:
    if chars <= 0:
        return "空白"
    if chars < 1000:
        return "1-999字"
    if chars < 5000:
        return "1000-4999字"
    if chars < 15000:
        return "5000-14999字"
    return "15000字以上"


def chart_items(
    counter: Counter[str],
    limit: int | None = None,
    order: list[str] | None = None,
) -> list[dict[str, Any]]:
    if order:
        labels = [label for label in order if label in counter]
        labels.extend(sorted(label for label in counter if label not in set(order)))
        items = [(label, counter[label]) for label in labels]
    else:
        items = counter.most_common(limit)
    if limit is not None and not order:
        items = items[:limit]
    return [{"label": label, "value": value} for label, value in items]


def metric(label: str, value: str, foot: str) -> str:
    return (
        '<article class="metric">'
        f'<div class="metric-label">{html_lib.escape(label)}</div>'
        f'<div class="metric-value">{html_lib.escape(value)}</div>'
        f'<div class="metric-foot">{html_lib.escape(foot)}</div>'
        "</article>"
    )


def fmt_int(value: int | float) -> str:
    return f"{int(value):,}"


def percentage(part: int, total: int) -> float:
    if total <= 0:
        return 0.0
    return round(part / total * 100, 1)


def to_int(value: Any) -> int:
    try:
        if value in (None, ""):
            return 0
        return int(float(value))
    except (TypeError, ValueError):
        return 0


def _private_use_count(value: str) -> int:
    return sum(1 for char in value if 0xE000 <= ord(char) <= 0xF8FF)


def _mojibake_marker_count(value: str) -> int:
    return sum(1 for char in value if char in MOJIBAKE_MARKERS)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Build a static dashboard for rysxai transfer-major policies."
    )
    parser.add_argument("--jsonl", type=Path, default=DEFAULT_JSONL_PATH)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_PATH)
    args = parser.parse_args(argv)

    output_path = write_dashboard(args.jsonl, args.output)
    print(f"wrote transfer policy dashboard: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
