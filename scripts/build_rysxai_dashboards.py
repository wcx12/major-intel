# -*- coding: utf-8 -*-
import csv
import html
import json
import statistics
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROC_DIR = ROOT / "data" / "processed" / "rysxai"
SEED_FILE = ROOT / "data" / "seeds" / "rysxai_professions.full.csv"
CIVIL_FILE = ROOT / "data" / "processed" / "rysxai_civil_service_2026.csv"
REPORT_DIR = ROOT / "reports" / "rysxai"

BENKE = "本科"
ZHUANKE = "专科"


def read_seed():
    with SEED_FILE.open("r", encoding="utf-8-sig", newline="") as f:
        return {int(row["rysxai_profession_id"]): row for row in csv.DictReader(f)}


def first_value(items, region, key):
    for item in items:
        if item.get("region") == region:
            return item.get(key)
    return None


def to_int(value, default=0):
    try:
        if value in (None, ""):
            return default
        return int(float(value))
    except (TypeError, ValueError):
        return default


def to_float(value):
    try:
        if value in (None, ""):
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def build_market_records(level):
    seed_by_id = read_seed()
    records = []
    for path in PROC_DIR.glob("profession_*_market_snapshot.json"):
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        profession = data.get("profession") or {}
        if profession.get("level") != level:
            continue

        profession_id = int(profession.get("id"))
        seed = seed_by_id.get(profession_id, {})
        macro = data.get("macro_employment") or {}
        demand = data.get("demand_ranking") or []
        salary = data.get("salary_ranking") or []
        records.append(
            {
                "id": profession_id,
                "name": profession.get("name") or seed.get("major_name") or "",
                "code": profession.get("code") or seed.get("major_code") or "",
                "level": level,
                "category": seed.get("category") or "",
                "subject": seed.get("subject") or "",
                "degree": profession.get("degree") or seed.get("degree") or "",
                "limitYear": profession.get("limit_year") or seed.get("limit_year") or "",
                "heat": to_int(seed.get("heat")),
                "isHot": str(seed.get("is_hot")).lower() == "true",
                "selectionAdvice": profession.get("selection_advice") or "",
                "capturedAt": data.get("captured_at") or "",
                "nationalDemand": first_value(demand, "全国", "demand_count"),
                "nationalSalary": first_value(salary, "全国", "monthly_salary_reference"),
                "jobSampleReported": data.get("job_posting_sample_total_reported"),
                "jobSampleCount": data.get("job_posting_sample_count"),
                "topIndustries": (macro.get("industry_distribution") or [])[:6],
                "topRegions": (macro.get("region_distribution") or [])[:6],
                "topJobs": (macro.get("job_direction_distribution") or [])[:6],
                "demandRanking": demand[:10],
                "salaryRanking": salary[:10],
                "warnings": data.get("warnings") or [],
                "report": f"profession_{profession_id}_market_report.md",
            }
        )
    records.sort(key=lambda r: (r["category"], r["subject"], r["code"]))
    return records


def build_market_payload(level):
    records = build_market_records(level)
    salary_values = [r["nationalSalary"] for r in records if isinstance(r["nationalSalary"], (int, float))]
    demand_values = [r["nationalDemand"] for r in records if isinstance(r["nationalDemand"], (int, float))]
    industry_counts = Counter()
    region_counts = Counter()
    empty_jobs = 0
    empty_industry = 0
    for record in records:
        if not record["jobSampleCount"]:
            empty_jobs += 1
        if not record["topIndustries"]:
            empty_industry += 1
        for item in record["topIndustries"][:3]:
            label = item.get("label")
            if label and label not in ("其他", "其他行业"):
                industry_counts[label] += 1
        for item in record["topRegions"][:3]:
            label = item.get("label")
            if label and label != "其他地区":
                region_counts[label] += 1

    categories = sorted({r["category"] for r in records if r["category"]})
    subjects = sorted({r["subject"] for r in records if r["subject"]})
    return {
        "summary": {
            "level": level,
            "total": len(records),
            "categoryCount": len(categories),
            "subjectCount": len(subjects),
            "salaryCoverage": len(salary_values),
            "demandCoverage": len(demand_values),
            "emptyJobSampleCount": empty_jobs,
            "emptyIndustryCount": empty_industry,
            "avgSalary": round(sum(salary_values) / len(salary_values)) if salary_values else None,
            "medianSalary": round(statistics.median(salary_values)) if salary_values else None,
            "avgDemand": round(sum(demand_values) / len(demand_values)) if demand_values else None,
            "latestCapturedAt": max((r["capturedAt"] for r in records if r["capturedAt"]), default=""),
        },
        "categories": categories,
        "subjects": subjects,
        "charts": {
            "categoryCounts": Counter(r["category"] or "未分类" for r in records).most_common(),
            "topIndustries": industry_counts.most_common(14),
            "topRegions": region_counts.most_common(14),
        },
        "records": records,
    }


def read_civil_rows():
    with CIVIL_FILE.open("r", encoding="utf-8-sig", newline="") as f:
        raw_rows = list(csv.DictReader(f))
    rows = []
    for row in raw_rows:
        ratio = to_float(row.get("ratio"))
        rows.append(
            {
                "id": row.get("id") or "",
                "year": row.get("year") or "",
                "departmentName": row.get("department_name") or "",
                "subDepartment": row.get("sub_department") or "",
                "jobName": row.get("job_name") or "",
                "jobIntro": row.get("job_intro") or "",
                "positionCode": row.get("position_code") or "",
                "sheetType": row.get("sheet_type") or "",
                "departmentLevel": row.get("department_level") or "",
                "examType": row.get("exam_type") or "",
                "province": row.get("province") or "",
                "workLocation": row.get("work_location") or "",
                "planNum": to_int(row.get("plan_num")),
                "applyNum": to_int(row.get("apply_num")),
                "ratio": ratio,
                "profession": row.get("profession") or "",
                "educationLevel": row.get("education_level") or "",
                "degreeRequirement": row.get("degree_requirement") or "",
                "identity": row.get("identity") or "",
                "workYear": row.get("work_year") or "",
                "workExperience": row.get("work_experience") or "",
                "needTest": row.get("need_test") or "",
                "interviewRatio": row.get("interview_ratio") or "",
                "residenceLocation": row.get("residence_location") or "",
                "remark": row.get("remark") or "",
                "isNewGraduate": str(row.get("is_new_graduate") or "").lower() == "true",
                "departmentWebsite": row.get("department_website") or "",
                "phone": row.get("phone") or "",
                "radar": parse_radar(row.get("wuweitu") or ""),
            }
        )
    return rows


def parse_radar(raw):
    try:
        data = json.loads(raw)
        if len(data) < 4:
            return None
        labels = [item.get("name", "") for item in data[1]]
        job_scores = data[2]
        avg_scores = data[3]
        return {"labels": labels, "job": job_scores, "average": avg_scores}
    except (TypeError, ValueError, json.JSONDecodeError):
        return None


def build_civil_payload():
    rows = read_civil_rows()
    plans = [r["planNum"] for r in rows]
    applies = [r["applyNum"] for r in rows]
    ratios = [r["ratio"] for r in rows if isinstance(r["ratio"], (int, float))]
    province_counts = Counter(r["province"] or "未标注" for r in rows)
    education_counts = Counter(r["educationLevel"] or "未标注" for r in rows)
    level_counts = Counter(r["departmentLevel"] or "未标注" for r in rows)
    exam_counts = Counter(r["examType"] or "未标注" for r in rows)
    dept_counts = Counter(r["departmentName"] or "未标注" for r in rows)
    return {
        "summary": {
            "total": len(rows),
            "planSum": sum(plans),
            "applySum": sum(applies),
            "avgRatio": round(statistics.mean(ratios), 1) if ratios else None,
            "medianRatio": round(statistics.median(ratios), 1) if ratios else None,
            "maxRatio": max(ratios) if ratios else None,
            "ratioCoverage": len(ratios),
            "newGraduateCount": sum(1 for r in rows if r["isNewGraduate"]),
            "topProvince": province_counts.most_common(1)[0][0] if province_counts else "",
        },
        "filters": {
            "provinces": sorted({r["province"] for r in rows if r["province"]}),
            "educationLevels": sorted({r["educationLevel"] for r in rows if r["educationLevel"]}),
            "departmentLevels": sorted({r["departmentLevel"] for r in rows if r["departmentLevel"]}),
            "examTypes": sorted({r["examType"] for r in rows if r["examType"]}),
        },
        "charts": {
            "topProvinces": province_counts.most_common(18),
            "educationLevels": education_counts.most_common(),
            "departmentLevels": level_counts.most_common(),
            "examTypes": exam_counts.most_common(),
            "topDepartments": dept_counts.most_common(20),
        },
        "records": rows,
    }


def safe_json(data):
    return json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c")


COMMON_CSS = """
:root {
  --bg:#f5f7fa; --panel:#fff; --text:#17212f; --muted:#657386; --line:#dce4ec;
  --blue:#0b66c3; --green:#047857; --orange:#b45309; --red:#b42318;
  --shadow:0 8px 24px rgba(24, 39, 58, .07);
}
* { box-sizing:border-box; }
html { background:var(--bg); }
body { margin:0; background:var(--bg); color:var(--text); font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","Microsoft YaHei",sans-serif; }
a { color:var(--blue); text-decoration:none; }
.topbar { position:sticky; top:0; z-index:5; background:rgba(255,255,255,.96); border-bottom:1px solid var(--line); }
.top-inner,.page { max-width:1440px; margin:0 auto; padding:16px 24px; }
.top-inner { display:grid; grid-template-columns:1fr auto; gap:16px; align-items:end; }
.nav { display:flex; gap:8px; flex-wrap:wrap; justify-content:flex-end; }
.nav a { height:34px; display:inline-flex; align-items:center; padding:0 10px; border:1px solid var(--line); border-radius:6px; background:white; font-size:13px; color:#354052; }
.nav a.active { background:#e8f2fd; border-color:#bdd8f5; color:#084e96; }
h1 { margin:0; font-size:26px; line-height:1.2; letter-spacing:0; }
h2 { margin:0; font-size:20px; letter-spacing:0; }
.sub,.note { color:var(--muted); font-size:13px; line-height:1.55; }
.sub { margin-top:6px; }
.page { display:grid; gap:18px; padding-top:22px; padding-bottom:42px; }
.stats { display:grid; grid-template-columns:repeat(6,minmax(120px,1fr)); gap:12px; }
.stat,.panel,.chart,.card { background:var(--panel); border:1px solid var(--line); border-radius:8px; box-shadow:var(--shadow); }
.stat { padding:14px; min-height:78px; }
.label { color:var(--muted); font-size:12px; margin-bottom:8px; }
.value { font-size:24px; font-weight:760; line-height:1; }
.controls { display:flex; flex-wrap:wrap; gap:10px; }
input,select { height:38px; min-width:160px; border:1px solid var(--line); border-radius:6px; padding:0 11px; background:white; color:var(--text); font-size:14px; }
input { min-width:300px; }
.charts { display:grid; grid-template-columns:repeat(3,1fr); gap:12px; }
.chart { padding:14px; min-height:210px; }
.chart h3 { margin:0 0 10px; font-size:14px; }
.bar { display:grid; grid-template-columns:minmax(88px,145px) 1fr auto; gap:10px; align-items:center; padding:4px 0; font-size:13px; }
.bar-name { overflow:hidden; white-space:nowrap; text-overflow:ellipsis; }
.track { height:8px; border-radius:999px; overflow:hidden; background:#e7edf3; }
.fill { height:100%; border-radius:999px; background:var(--blue); min-width:2px; }
.fill.green { background:var(--green); }
.fill.orange { background:var(--orange); }
.grid { display:grid; grid-template-columns:1.15fr .85fr; gap:18px; align-items:start; }
.head { padding:14px 16px; display:flex; justify-content:space-between; gap:12px; border-bottom:1px solid var(--line); }
.title { font-weight:720; font-size:15px; }
.table-wrap { max-height:690px; overflow:auto; }
table { width:100%; border-collapse:collapse; font-size:13px; }
th { position:sticky; top:0; z-index:1; background:#eef3f8; text-align:left; color:#3d4a5c; font-size:12px; padding:10px 12px; border-bottom:1px solid var(--line); }
td { padding:10px 12px; border-bottom:1px solid #edf1f5; vertical-align:top; }
tr { cursor:pointer; }
tr:hover td,tr.active td { background:#eef7ff; }
.code { font-family:ui-monospace,SFMono-Regular,Consolas,monospace; color:#3c4a5f; }
.badge { display:inline-flex; align-items:center; min-height:22px; padding:2px 8px; border-radius:999px; background:#e7f0fa; color:#155c9e; font-size:12px; white-space:nowrap; }
.badge.green { background:#e2f4ea; color:var(--green); }
.badge.orange { background:#fff2dc; color:var(--orange); }
.badge.red { background:#fde8e7; color:var(--red); }
.detail { padding:16px; }
.detail h2 { margin:0 0 6px; font-size:22px; letter-spacing:0; }
.meta { display:flex; flex-wrap:wrap; gap:8px; margin:10px 0 16px; }
.kv { display:grid; grid-template-columns:92px 1fr; gap:8px; padding:8px 0; border-bottom:1px solid #eef2f5; font-size:13px; }
.kv span:first-child { color:var(--muted); }
.section { margin-top:18px; }
.section-title { font-size:14px; font-weight:720; margin-bottom:10px; }
.rank-grid { display:grid; grid-template-columns:1fr 1fr; gap:12px; }
.rank-card { background:#f0f4f8; border:1px solid var(--line); border-radius:8px; padding:12px; }
.rank-row { display:flex; justify-content:space-between; gap:12px; padding:6px 0; border-bottom:1px solid rgba(0,0,0,.06); font-size:13px; }
.rank-row:last-child { border-bottom:0; }
.empty { padding:28px; text-align:center; color:var(--muted); }
.cards { display:grid; grid-template-columns:repeat(3,1fr); gap:14px; }
.card { padding:18px; display:grid; gap:12px; }
.card-title { font-size:18px; font-weight:760; }
.card-actions { display:flex; flex-wrap:wrap; gap:8px; }
.button { height:36px; display:inline-flex; align-items:center; justify-content:center; padding:0 12px; border-radius:6px; border:1px solid #b8d7f6; background:#e8f2fd; color:#084e96; font-size:13px; }
.data-list { display:grid; gap:10px; }
.data-row { display:grid; grid-template-columns:210px 1fr; gap:10px; padding:12px 0; border-bottom:1px solid var(--line); font-size:14px; }
.data-row:last-child { border-bottom:0; }
.muted { color:var(--muted); }
.nowrap { white-space:nowrap; }
.clamp { display:-webkit-box; -webkit-line-clamp:2; -webkit-box-orient:vertical; overflow:hidden; }
@media (max-width:1120px) {
  .stats { grid-template-columns:repeat(3,1fr); }
  .charts { grid-template-columns:1fr 1fr; }
  .grid,.top-inner,.cards { grid-template-columns:1fr; }
  .nav { justify-content:flex-start; }
}
@media (max-width:720px) {
  .top-inner,.page { padding-left:14px; padding-right:14px; }
  .stats,.charts,.rank-grid { grid-template-columns:1fr; }
  input,select { width:100%; min-width:0; }
  th.hide-sm,td.hide-sm { display:none; }
  .data-row { grid-template-columns:1fr; }
}
"""


def wrap_page(title, subtitle, active, body, payload, script):
    nav_items = [
        ("index.html", "总入口", "index"),
        ("undergraduate_market_overview.html", "本科就业", "benke"),
        ("vocational_market_overview.html", "专科就业", "zhuanke"),
        ("civil_service_2026_overview.html", "考公岗位", "civil"),
    ]
    nav = "\n".join(
        f'<a class="{"active" if key == active else ""}" href="{href}">{label}</a>'
        for href, label, key in nav_items
    )
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>{html.escape(title)}</title>
<style>{COMMON_CSS}</style>
</head>
<body>
<header class="topbar">
  <div class="top-inner">
    <div>
      <h1>{html.escape(title)}</h1>
      <div class="sub">{html.escape(subtitle)}</div>
    </div>
    <nav class="nav">{nav}</nav>
  </div>
</header>
<main class="page">
{body}
</main>
<script id="payload" type="application/json">{safe_json(payload)}</script>
<script>{script}</script>
</body>
</html>
"""


MARKET_BODY = """
  <section id="stats" class="stats"></section>
  <section class="panel">
    <div class="head">
      <div>
        <div class="title">筛选专业</div>
        <div class="note">按名称、代码、门类、专业类快速定位，点击列表行查看就业市场细节。</div>
      </div>
      <div id="coverageNote" class="note"></div>
    </div>
    <div class="detail controls">
      <input id="search" placeholder="搜索专业名称、代码、门类、专业类" />
      <select id="category"><option value="">全部门类</option></select>
      <select id="sort">
        <option value="code">按专业代码</option>
        <option value="heat">按热度</option>
        <option value="salary">按全国薪资</option>
        <option value="demand">按全国需求</option>
      </select>
    </div>
  </section>
  <section id="charts" class="charts"></section>
  <section class="grid">
    <div class="panel">
      <div class="head"><div class="title">专业列表</div><div id="resultCount" class="note"></div></div>
      <div class="table-wrap">
        <table>
          <thead><tr><th>代码</th><th>专业</th><th>门类</th><th class="hide-sm">专业类</th><th>全国薪资</th><th class="hide-sm">全国需求</th></tr></thead>
          <tbody id="tbody"></tbody>
        </table>
      </div>
    </div>
    <aside class="panel">
      <div class="head"><div class="title">专业详情</div><div class="note"><a id="reportLink" href="#">单专业报告</a></div></div>
      <div id="detail" class="detail"></div>
    </aside>
  </section>
"""


MARKET_SCRIPT = r"""
const payload = JSON.parse(document.getElementById('payload').textContent);
const records = payload.records;
let activeId = records[0] && records[0].id;
const fmt = new Intl.NumberFormat('zh-CN');
const byId = id => document.getElementById(id);
const esc = text => String(text ?? '').replace(/[&<>"']/g, ch => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));
const number = n => Number.isFinite(Number(n)) ? fmt.format(Number(n)) : '-';
const money = n => Number.isFinite(Number(n)) ? fmt.format(Number(n)) : '-';
function stat(label,value) {
  return `<div class="stat"><div class="label">${label}</div><div class="value">${value}</div></div>`;
}
function renderStats() {
  const s = payload.summary;
  byId('stats').innerHTML = [
    stat(`${s.level}专业`, number(s.total)),
    stat('专业门类', number(s.categoryCount)),
    stat('专业类', number(s.subjectCount)),
    stat('薪资覆盖', `${number(s.salaryCoverage)}/${number(s.total)}`),
    stat('全国薪资中位数', money(s.medianSalary)),
    stat('全国需求均值', number(s.avgDemand))
  ].join('');
  byId('coverageNote').textContent = `岗位样本为空：${number(s.emptyJobSampleCount)} 个；行业分布为空：${number(s.emptyIndustryCount)} 个`;
}
function bars(title, rows, color) {
  const max = Math.max(...rows.map(x => x[1]), 1);
  return `<div class="chart"><h3>${title}</h3>` + rows.map(([label,value]) =>
    `<div class="bar"><div class="bar-name" title="${esc(label)}">${esc(label)}</div><div class="track"><div class="fill ${color || ''}" style="width:${Math.max(3,value/max*100)}%"></div></div><div>${number(value)}</div></div>`
  ).join('') + '</div>';
}
function renderCharts() {
  byId('charts').innerHTML = [
    bars('专业门类数量', payload.charts.categoryCounts.slice(0,14), ''),
    bars('高频就业方向/行业', payload.charts.topIndustries.slice(0,14), 'green'),
    bars('高频城市分布', payload.charts.topRegions.slice(0,14), 'orange')
  ].join('');
}
function populateFilters() {
  byId('category').insertAdjacentHTML('beforeend', payload.categories.map(c => `<option value="${esc(c)}">${esc(c)}</option>`).join(''));
}
function currentRows() {
  const q = byId('search').value.trim().toLowerCase();
  const category = byId('category').value;
  const sort = byId('sort').value;
  let rows = records.filter(r => {
    const text = `${r.name} ${r.code} ${r.category} ${r.subject}`.toLowerCase();
    return (!q || text.includes(q)) && (!category || r.category === category);
  });
  rows.sort((a,b) => {
    if (sort === 'heat') return (b.heat || 0) - (a.heat || 0);
    if (sort === 'salary') return (b.nationalSalary || -1) - (a.nationalSalary || -1);
    if (sort === 'demand') return (b.nationalDemand || -1) - (a.nationalDemand || -1);
    return String(a.code).localeCompare(String(b.code), 'zh-CN');
  });
  return rows;
}
function renderTable() {
  const rows = currentRows();
  if (!rows.find(r => r.id === activeId) && rows[0]) activeId = rows[0].id;
  byId('resultCount').textContent = `匹配 ${number(rows.length)} 个专业`;
  byId('tbody').innerHTML = rows.map(r => `<tr data-id="${r.id}" class="${r.id === activeId ? 'active' : ''}">
    <td class="code">${esc(r.code)}</td>
    <td><strong>${esc(r.name)}</strong><div class="note">${r.isHot ? '热门专业' : ''}</div></td>
    <td>${esc(r.category || '-')}</td>
    <td class="hide-sm">${esc(r.subject || '-')}</td>
    <td>${money(r.nationalSalary)}</td>
    <td class="hide-sm">${number(r.nationalDemand)}</td>
  </tr>`).join('') || '<tr><td colspan="6" class="empty">没有匹配到专业</td></tr>';
  byId('tbody').querySelectorAll('tr[data-id]').forEach(row => row.addEventListener('click', () => {
    activeId = Number(row.dataset.id);
    renderTable();
    renderDetail();
  }));
}
function rankRows(rows, valueKey, suffix) {
  return (rows || []).slice(0,8).map(item => `<div class="rank-row"><span>${esc(item.region || item.label || '-')}</span><strong>${number(item[valueKey])}${suffix || ''}</strong></div>`).join('') || '<div class="note">暂无数据</div>';
}
function percentRows(rows) {
  return (rows || []).slice(0,8).map(item => `<div class="rank-row"><span>${esc(item.label || '-')}</span><strong>${Number.isFinite(Number(item.rate_percent)) ? Number(item.rate_percent).toFixed(1) + '%' : '-'}</strong></div>`).join('') || '<div class="note">暂无数据</div>';
}
function renderDetail() {
  const r = records.find(x => x.id === activeId) || records[0];
  if (!r) {
    byId('detail').innerHTML = '<div class="empty">暂无数据</div>';
    return;
  }
  byId('reportLink').href = r.report;
  byId('detail').innerHTML = `
    <h2>${esc(r.name)}</h2>
    <div class="note code">${esc(r.code)} · ${esc(r.category || '-')} · ${esc(r.subject || '-')}</div>
    <div class="meta">
      <span class="badge">${esc(r.level)}</span>
      <span class="badge green">学制 ${esc(r.limitYear || '-')}</span>
      <span class="badge orange">热度 ${number(r.heat)}</span>
      ${r.isHot ? '<span class="badge red">热门</span>' : ''}
    </div>
    <div class="kv"><span>全国薪资</span><strong>${money(r.nationalSalary)}</strong></div>
    <div class="kv"><span>全国需求</span><strong>${number(r.nationalDemand)}</strong></div>
    <div class="kv"><span>岗位样本</span><strong>${number(r.jobSampleCount)} / ${number(r.jobSampleReported)}</strong></div>
    <div class="kv"><span>选科建议</span><div>${esc(r.selectionAdvice || '暂无')}</div></div>
    <div class="section">
      <div class="section-title">就业方向与地区</div>
      <div class="rank-grid">
        <div class="rank-card"><div class="section-title">方向/行业占比</div>${percentRows(r.topJobs.length ? r.topJobs : r.topIndustries)}</div>
        <div class="rank-card"><div class="section-title">地区占比</div>${percentRows(r.topRegions)}</div>
      </div>
    </div>
    <div class="section">
      <div class="section-title">城市排行</div>
      <div class="rank-grid">
        <div class="rank-card"><div class="section-title">需求</div>${rankRows(r.demandRanking, 'demand_count')}</div>
        <div class="rank-card"><div class="section-title">薪资</div>${rankRows(r.salaryRanking, 'monthly_salary_reference')}</div>
      </div>
    </div>`;
}
['search','category','sort'].forEach(id => byId(id).addEventListener('input', () => { renderTable(); renderDetail(); }));
renderStats();
renderCharts();
populateFilters();
renderTable();
renderDetail();
"""


CIVIL_BODY = """
  <section id="stats" class="stats"></section>
  <section class="panel">
    <div class="head">
      <div>
        <div class="title">筛选岗位</div>
        <div class="note">按岗位、单位、专业要求、地区搜索。列表只渲染前 600 条匹配结果，避免浏览器卡顿。</div>
      </div>
      <div id="coverageNote" class="note"></div>
    </div>
    <div class="detail controls">
      <input id="search" placeholder="搜索岗位、单位、专业要求、地区" />
      <select id="province"><option value="">全部省份</option></select>
      <select id="education"><option value="">全部学历</option></select>
      <select id="sort">
        <option value="ratioDesc">竞争比高到低</option>
        <option value="ratioAsc">竞争比低到高</option>
        <option value="apply">报名人数</option>
        <option value="plan">招录人数</option>
      </select>
    </div>
  </section>
  <section id="charts" class="charts"></section>
  <section class="grid">
    <div class="panel">
      <div class="head"><div class="title">岗位列表</div><div id="resultCount" class="note"></div></div>
      <div class="table-wrap">
        <table>
          <thead><tr><th>岗位</th><th>省份</th><th>招录</th><th>报名</th><th>竞争比</th><th class="hide-sm">学历</th></tr></thead>
          <tbody id="tbody"></tbody>
        </table>
      </div>
    </div>
    <aside class="panel">
      <div class="head"><div class="title">岗位详情</div><div class="note">2026 国考</div></div>
      <div id="detail" class="detail"></div>
    </aside>
  </section>
"""


CIVIL_SCRIPT = r"""
const payload = JSON.parse(document.getElementById('payload').textContent);
const records = payload.records;
let activeId = records[0] && records[0].id;
const fmt = new Intl.NumberFormat('zh-CN');
const byId = id => document.getElementById(id);
const esc = text => String(text ?? '').replace(/[&<>"']/g, ch => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));
const number = n => Number.isFinite(Number(n)) ? fmt.format(Number(n)) : '-';
const ratio = n => Number.isFinite(Number(n)) ? Number(n).toFixed(1) : '-';
function stat(label,value) {
  return `<div class="stat"><div class="label">${label}</div><div class="value">${value}</div></div>`;
}
function renderStats() {
  const s = payload.summary;
  byId('stats').innerHTML = [
    stat('岗位数', number(s.total)),
    stat('招录人数', number(s.planSum)),
    stat('报名人数', number(s.applySum)),
    stat('竞争比中位数', ratio(s.medianRatio)),
    stat('最高竞争比', ratio(s.maxRatio)),
    stat('限应届岗位', number(s.newGraduateCount))
  ].join('');
  byId('coverageNote').textContent = `竞争比覆盖：${number(s.ratioCoverage)} / ${number(s.total)}；岗位最多省份：${s.topProvince}`;
}
function bars(title, rows, color) {
  const max = Math.max(...rows.map(x => x[1]), 1);
  return `<div class="chart"><h3>${title}</h3>` + rows.map(([label,value]) =>
    `<div class="bar"><div class="bar-name" title="${esc(label)}">${esc(label)}</div><div class="track"><div class="fill ${color || ''}" style="width:${Math.max(3,value/max*100)}%"></div></div><div>${number(value)}</div></div>`
  ).join('') + '</div>';
}
function renderCharts() {
  byId('charts').innerHTML = [
    bars('岗位省份分布', payload.charts.topProvinces.slice(0,14), ''),
    bars('学历要求', payload.charts.educationLevels.slice(0,10), 'green'),
    bars('机构层级', payload.charts.departmentLevels, 'orange')
  ].join('');
}
function populateFilters() {
  byId('province').insertAdjacentHTML('beforeend', payload.filters.provinces.map(x => `<option value="${esc(x)}">${esc(x)}</option>`).join(''));
  byId('education').insertAdjacentHTML('beforeend', payload.filters.educationLevels.map(x => `<option value="${esc(x)}">${esc(x)}</option>`).join(''));
}
function currentRows() {
  const q = byId('search').value.trim().toLowerCase();
  const province = byId('province').value;
  const education = byId('education').value;
  const sort = byId('sort').value;
  let rows = records.filter(r => {
    const text = `${r.departmentName} ${r.subDepartment} ${r.jobName} ${r.positionCode} ${r.profession} ${r.province} ${r.workLocation}`.toLowerCase();
    return (!q || text.includes(q)) && (!province || r.province === province) && (!education || r.educationLevel === education);
  });
  rows.sort((a,b) => {
    if (sort === 'ratioAsc') return (a.ratio ?? 999999) - (b.ratio ?? 999999);
    if (sort === 'apply') return (b.applyNum || 0) - (a.applyNum || 0);
    if (sort === 'plan') return (b.planNum || 0) - (a.planNum || 0);
    return (b.ratio ?? -1) - (a.ratio ?? -1);
  });
  return rows;
}
function renderTable() {
  const rows = currentRows();
  if (!rows.find(r => r.id === activeId) && rows[0]) activeId = rows[0].id;
  const shown = rows.slice(0,600);
  byId('resultCount').textContent = `匹配 ${number(rows.length)} 个岗位，显示 ${number(shown.length)} 个`;
  byId('tbody').innerHTML = shown.map(r => `<tr data-id="${esc(r.id)}" class="${r.id === activeId ? 'active' : ''}">
    <td><strong>${esc(r.jobName)}</strong><div class="note clamp">${esc(r.departmentName)} · ${esc(r.subDepartment)}</div></td>
    <td>${esc(r.province || '-')}</td>
    <td>${number(r.planNum)}</td>
    <td>${number(r.applyNum)}</td>
    <td><strong>${ratio(r.ratio)}</strong></td>
    <td class="hide-sm">${esc(r.educationLevel || '-')}</td>
  </tr>`).join('') || '<tr><td colspan="6" class="empty">没有匹配到岗位</td></tr>';
  byId('tbody').querySelectorAll('tr[data-id]').forEach(row => row.addEventListener('click', () => {
    activeId = row.dataset.id;
    renderTable();
    renderDetail();
  }));
}
function radarRows(radar) {
  if (!radar) return '<div class="note">暂无评分数据</div>';
  return radar.labels.map((label, i) => `<div class="rank-row"><span>${esc(label)}</span><strong>${ratio(radar.job[i])} / ${ratio(radar.average[i])}</strong></div>`).join('');
}
function renderDetail() {
  const r = records.find(x => x.id === activeId) || records[0];
  if (!r) {
    byId('detail').innerHTML = '<div class="empty">暂无数据</div>';
    return;
  }
  byId('detail').innerHTML = `
    <h2>${esc(r.jobName)}</h2>
    <div class="note">${esc(r.departmentName)} · ${esc(r.subDepartment)} · <span class="code">${esc(r.positionCode)}</span></div>
    <div class="meta">
      <span class="badge">${esc(r.province || '-')}</span>
      <span class="badge green">招 ${number(r.planNum)}</span>
      <span class="badge orange">报名 ${number(r.applyNum)}</span>
      <span class="badge red">竞争比 ${ratio(r.ratio)}</span>
      ${r.isNewGraduate ? '<span class="badge">限应届</span>' : ''}
    </div>
    <div class="kv"><span>学历要求</span><strong>${esc(r.educationLevel || '-')}</strong></div>
    <div class="kv"><span>学位要求</span><strong>${esc(r.degreeRequirement || '-')}</strong></div>
    <div class="kv"><span>机构层级</span><div>${esc(r.departmentLevel || '-')} · ${esc(r.examType || '-')}</div></div>
    <div class="kv"><span>工作地点</span><div>${esc(r.workLocation || '-')}</div></div>
    <div class="kv"><span>政治面貌</span><div>${esc(r.identity || '-')}</div></div>
    <div class="kv"><span>基层年限</span><div>${esc(r.workYear || '-')}</div></div>
    <div class="section">
      <div class="section-title">专业要求</div>
      <div class="rank-card">${esc(r.profession || '不限')}</div>
    </div>
    <div class="section">
      <div class="section-title">岗位简介</div>
      <div class="rank-card">${esc(r.jobIntro || '暂无')}</div>
    </div>
    <div class="section">
      <div class="section-title">五维评分：本岗位 / 岗位平均</div>
      <div class="rank-card">${radarRows(r.radar)}</div>
    </div>
    <div class="section">
      <div class="section-title">备注</div>
      <div class="rank-card">${esc(r.remark || '暂无').replace(/\n/g, '<br>')}</div>
    </div>`;
}
['search','province','education','sort'].forEach(id => byId(id).addEventListener('input', () => { renderTable(); renderDetail(); }));
renderStats();
renderCharts();
populateFilters();
renderTable();
renderDetail();
"""


def build_market_page(payload, filename, title, active_key):
    latest = payload["summary"]["latestCapturedAt"] or "未标注"
    subtitle = f"数据源：data/processed/rysxai；最近抓取：{latest}；页面内嵌数据，可离线打开。"
    (REPORT_DIR / filename).write_text(wrap_page(title, subtitle, active_key, MARKET_BODY, payload, MARKET_SCRIPT), encoding="utf-8")


def build_civil_page(payload):
    subtitle = "数据源：data/processed/rysxai_civil_service_2026.csv；页面内嵌数据，可离线打开。"
    (REPORT_DIR / "civil_service_2026_overview.html").write_text(
        wrap_page("2026 考公岗位总览", subtitle, "civil", CIVIL_BODY, payload, CIVIL_SCRIPT),
        encoding="utf-8",
    )


def build_index_page(benke_payload, zhuanke_payload, civil_payload):
    b = benke_payload["summary"]
    z = zhuanke_payload["summary"]
    c = civil_payload["summary"]
    body = f"""
  <section class="cards">
    <article class="card">
      <div class="card-title">本科就业市场</div>
      <div class="note">覆盖 {b["total"]} 个本科专业，薪资覆盖 {b["salaryCoverage"]} 个，岗位样本为空 {b["emptyJobSampleCount"]} 个。</div>
      <div class="stats">
        <div class="stat"><div class="label">专业</div><div class="value">{b["total"]}</div></div>
        <div class="stat"><div class="label">门类</div><div class="value">{b["categoryCount"]}</div></div>
        <div class="stat"><div class="label">薪资中位数</div><div class="value">{b["medianSalary"] or "-"}</div></div>
      </div>
      <div class="card-actions"><a class="button" href="undergraduate_market_overview.html">打开本科总览</a></div>
    </article>
    <article class="card">
      <div class="card-title">专科就业市场</div>
      <div class="note">覆盖 {z["total"]} 个专科专业，薪资覆盖 {z["salaryCoverage"]} 个，岗位样本为空 {z["emptyJobSampleCount"]} 个。</div>
      <div class="stats">
        <div class="stat"><div class="label">专业</div><div class="value">{z["total"]}</div></div>
        <div class="stat"><div class="label">门类</div><div class="value">{z["categoryCount"]}</div></div>
        <div class="stat"><div class="label">薪资中位数</div><div class="value">{z["medianSalary"] or "-"}</div></div>
      </div>
      <div class="card-actions"><a class="button" href="vocational_market_overview.html">打开专科总览</a></div>
    </article>
    <article class="card">
      <div class="card-title">2026 考公岗位</div>
      <div class="note">覆盖 {c["total"]} 个岗位，招录 {c["planSum"]} 人，报名 {c["applySum"]} 人。</div>
      <div class="stats">
        <div class="stat"><div class="label">岗位</div><div class="value">{c["total"]}</div></div>
        <div class="stat"><div class="label">招录</div><div class="value">{c["planSum"]}</div></div>
        <div class="stat"><div class="label">中位竞争比</div><div class="value">{c["medianRatio"] or "-"}</div></div>
      </div>
      <div class="card-actions"><a class="button" href="civil_service_2026_overview.html">打开考公总览</a></div>
    </article>
  </section>
  <section class="panel">
    <div class="head">
      <div class="title">现在数据可以这样分层</div>
      <div class="note">原始层不动，展示层按主题拆开，后面要导入本地数据库也更清楚。</div>
    </div>
    <div class="detail data-list">
      <div class="data-row"><strong>原始抓取</strong><div><span class="code">data/raw/rysxai/full_benke_20260519</span>、<span class="code">data/raw/rysxai/full_zhuanke_20260519</span>、<span class="code">data/raw/rysxai_civil_service_2026.jsonl</span></div></div>
      <div class="data-row"><strong>清洗结果</strong><div><span class="code">data/processed/rysxai/profession_*_market_snapshot.json</span> 和 <span class="code">data/processed/rysxai_civil_service_2026.csv</span></div></div>
      <div class="data-row"><strong>展示报表</strong><div>本科就业、专科就业、考公岗位三张总览页都放在 <span class="code">reports/rysxai</span>，每张都是可离线打开的单 HTML 文件。</div></div>
      <div class="data-row"><strong>后续入库</strong><div>建议把就业快照按 <span class="code">profession_id + level</span> 存，考公岗位按 <span class="code">id / position_code</span> 存；专业和岗位之间再做一张“专业要求解析/匹配表”。</div></div>
    </div>
  </section>
"""
    payload = {"benke": b, "zhuanke": z, "civil": c}
    (REPORT_DIR / "index.html").write_text(
        wrap_page("专业与考公数据整理总入口", "本地 reports/rysxai 汇总页，所有链接指向同目录下的静态报表。", "index", body, payload, ""),
        encoding="utf-8",
    )


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        pass

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    benke_payload = build_market_payload(BENKE)
    zhuanke_payload = build_market_payload(ZHUANKE)
    civil_payload = build_civil_payload()

    build_market_page(benke_payload, "undergraduate_market_overview.html", "本科就业市场总览", "benke")
    build_market_page(zhuanke_payload, "vocational_market_overview.html", "专科就业市场总览", "zhuanke")
    build_civil_page(civil_payload)
    build_index_page(benke_payload, zhuanke_payload, civil_payload)

    print(json.dumps({
        "reports": {
            "index": str(REPORT_DIR / "index.html"),
            "undergraduate": str(REPORT_DIR / "undergraduate_market_overview.html"),
            "vocational": str(REPORT_DIR / "vocational_market_overview.html"),
            "civil": str(REPORT_DIR / "civil_service_2026_overview.html"),
        },
        "summary": {
            "undergraduate": benke_payload["summary"],
            "vocational": zhuanke_payload["summary"],
            "civil": civil_payload["summary"],
        },
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
