import csv
import html
import json
import statistics
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
PROC_DIR = ROOT / "data" / "processed" / "rysxai"
SEED_FILE = ROOT / "data" / "seeds" / "rysxai_professions.full.csv"
OUT_FILE = ROOT / "reports" / "rysxai" / "undergraduate_market_overview.html"
BENKE = "\u672c\u79d1"


def load_seed():
    with SEED_FILE.open("r", encoding="utf-8-sig", newline="") as f:
        return {int(row["rysxai_profession_id"]): row for row in csv.DictReader(f)}


def first_value(items, region, key):
    for item in items:
        if item.get("region") == region:
            return item.get(key)
    return None


def build_records():
    seed_by_id = load_seed()
    records = []
    for path in PROC_DIR.glob("profession_*_market_snapshot.json"):
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        profession = data.get("profession") or {}
        if profession.get("level") != BENKE:
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
                "category": seed.get("category") or "",
                "subject": seed.get("subject") or "",
                "degree": profession.get("degree") or seed.get("degree") or "",
                "limitYear": profession.get("limit_year") or seed.get("limit_year") or "",
                "heat": int(seed.get("heat") or 0),
                "isHot": str(seed.get("is_hot")).lower() == "true",
                "selectionAdvice": profession.get("selection_advice") or "",
                "capturedAt": data.get("captured_at") or "",
                "nationalDemand": first_value(demand, "\u5168\u56fd", "demand_count"),
                "nationalSalary": first_value(salary, "\u5168\u56fd", "monthly_salary_reference"),
                "jobSampleReported": data.get("job_posting_sample_total_reported"),
                "jobSampleCount": data.get("job_posting_sample_count"),
                "topIndustries": (macro.get("industry_distribution") or [])[:5],
                "topRegions": (macro.get("region_distribution") or [])[:5],
                "topJobs": (macro.get("job_direction_distribution") or [])[:5],
                "demandRanking": demand[:8],
                "salaryRanking": salary[:8],
                "warnings": data.get("warnings") or [],
                "report": f"profession_{profession_id}_market_report.md",
            }
        )

    records.sort(key=lambda r: (r["category"], r["subject"], r["code"]))
    return records


def build_payload(records):
    categories = sorted({r["category"] for r in records if r["category"]})
    salary_values = [r["nationalSalary"] for r in records if isinstance(r["nationalSalary"], (int, float))]
    demand_values = [r["nationalDemand"] for r in records if isinstance(r["nationalDemand"], (int, float))]

    industry_counts = Counter()
    region_counts = Counter()
    for record in records:
        for item in record["topIndustries"][:3]:
            label = item.get("label")
            if label and label not in ("\u5176\u4ed6", "\u5176\u4ed6\u884c\u4e1a"):
                industry_counts[label] += 1
        for item in record["topRegions"][:3]:
            label = item.get("label")
            if label and label != "\u5176\u4ed6\u5730\u533a":
                region_counts[label] += 1

    return {
        "summary": {
            "total": len(records),
            "categoryCount": len(categories),
            "subjectCount": len({r["subject"] for r in records if r["subject"]}),
            "salaryCoverage": len(salary_values),
            "demandCoverage": len(demand_values),
            "avgSalary": round(sum(salary_values) / len(salary_values)) if salary_values else None,
            "medianSalary": round(statistics.median(salary_values)) if salary_values else None,
            "avgDemand": round(sum(demand_values) / len(demand_values)) if demand_values else None,
            "latestCapturedAt": max((r["capturedAt"] for r in records if r["capturedAt"]), default=""),
        },
        "categories": categories,
        "charts": {
            "categoryCounts": Counter(r["category"] or "\u672a\u5206\u7c7b" for r in records).most_common(),
            "topIndustries": industry_counts.most_common(14),
            "topRegions": region_counts.most_common(14),
        },
        "records": records,
    }


def build_html(payload):
    payload_json = json.dumps(payload, ensure_ascii=False).replace("<", "\\u003c")
    latest = html.escape(payload["summary"]["latestCapturedAt"])
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>本科专业市场观察总览</title>
<style>
:root {{
  --bg:#f6f7f9; --panel:#fff; --muted:#667487; --line:#dce3ea;
  --text:#1d2733; --blue:#0b6bcb; --green:#047857; --orange:#b45309;
  --shadow:0 10px 30px rgba(24,39,58,.08);
}}
* {{ box-sizing:border-box; }}
body {{ margin:0; background:var(--bg); color:var(--text); font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","Microsoft YaHei",sans-serif; }}
.header {{ position:sticky; top:0; z-index:5; background:white; border-bottom:1px solid var(--line); }}
.header-inner,.main {{ max-width:1440px; margin:0 auto; padding:18px 24px; }}
.header-inner {{ display:grid; grid-template-columns:1fr auto; gap:16px; align-items:end; }}
h1 {{ margin:0; font-size:26px; line-height:1.2; letter-spacing:0; }}
.sub,.note {{ color:var(--muted); font-size:13px; }}
.sub {{ margin-top:6px; }}
.controls {{ display:flex; gap:10px; flex-wrap:wrap; justify-content:flex-end; }}
input,select {{ height:38px; min-width:170px; border:1px solid var(--line); border-radius:6px; padding:0 11px; background:white; color:var(--text); font-size:14px; }}
input {{ min-width:280px; }}
.main {{ display:grid; gap:18px; padding-top:22px; padding-bottom:40px; }}
.stats {{ display:grid; grid-template-columns:repeat(6,minmax(120px,1fr)); gap:12px; }}
.stat,.panel,.chart {{ background:var(--panel); border:1px solid var(--line); border-radius:8px; box-shadow:var(--shadow); }}
.stat {{ padding:14px; min-height:78px; }}
.label {{ color:var(--muted); font-size:12px; margin-bottom:8px; }}
.value {{ font-size:24px; font-weight:780; line-height:1; }}
.charts {{ display:grid; grid-template-columns:1fr 1fr; gap:12px; }}
.chart {{ padding:14px; }}
.chart h3 {{ margin:0 0 10px; font-size:14px; }}
.bar {{ display:grid; grid-template-columns:minmax(92px,150px) 1fr auto; gap:10px; align-items:center; padding:4px 0; font-size:13px; }}
.track {{ height:8px; border-radius:999px; overflow:hidden; background:#e7edf3; }}
.fill {{ height:100%; border-radius:999px; background:var(--blue); min-width:2px; }}
.fill.green {{ background:var(--green); }}
.grid {{ display:grid; grid-template-columns:1.15fr .85fr; gap:18px; align-items:start; }}
.head {{ padding:14px 16px; display:flex; justify-content:space-between; gap:12px; border-bottom:1px solid var(--line); }}
.title {{ font-weight:720; font-size:15px; }}
.table-wrap {{ max-height:650px; overflow:auto; }}
table {{ width:100%; border-collapse:collapse; font-size:13px; }}
th {{ position:sticky; top:0; background:#eef3f7; text-align:left; color:#3d4a5c; font-size:12px; padding:10px 12px; border-bottom:1px solid var(--line); }}
td {{ padding:10px 12px; border-bottom:1px solid #edf1f5; vertical-align:top; }}
tr {{ cursor:pointer; }}
tr:hover td,tr.active td {{ background:#eef7ff; }}
.code {{ font-family:ui-monospace,SFMono-Regular,Consolas,monospace; color:#3c4a5f; }}
.badge {{ display:inline-flex; align-items:center; height:22px; padding:0 8px; border-radius:999px; background:#e7f0fa; color:#155c9e; font-size:12px; white-space:nowrap; }}
.badge.green {{ background:#e2f4ea; color:var(--green); }}
.badge.orange {{ background:#fff2dc; color:var(--orange); }}
.detail {{ padding:16px; }}
.detail h2 {{ margin:0 0 6px; font-size:22px; letter-spacing:0; }}
.meta {{ display:flex; flex-wrap:wrap; gap:8px; margin:10px 0 16px; }}
.kv {{ display:grid; grid-template-columns:82px 1fr; gap:8px; padding:8px 0; border-bottom:1px solid #eef2f5; font-size:13px; }}
.kv span:first-child {{ color:var(--muted); }}
.section {{ margin-top:18px; }}
.section-title {{ font-size:14px; font-weight:720; margin-bottom:10px; }}
.rank-grid {{ display:grid; grid-template-columns:1fr 1fr; gap:12px; }}
.rank-card {{ background:#f0f4f8; border:1px solid var(--line); border-radius:8px; padding:12px; }}
.rank-row {{ display:flex; justify-content:space-between; gap:12px; padding:6px 0; border-bottom:1px solid rgba(0,0,0,.06); font-size:13px; }}
.rank-row:last-child {{ border-bottom:0; }}
a {{ color:var(--blue); text-decoration:none; }}
.empty {{ padding:28px; text-align:center; color:var(--muted); }}
@media (max-width:1100px) {{ .stats {{ grid-template-columns:repeat(3,1fr); }} .grid,.header-inner {{ grid-template-columns:1fr; }} .controls {{ justify-content:flex-start; }} }}
@media (max-width:720px) {{ .header-inner,.main {{ padding-left:14px; padding-right:14px; }} .stats,.charts,.rank-grid {{ grid-template-columns:1fr; }} input,select {{ width:100%; min-width:0; }} th:nth-child(4),td:nth-child(4),th:nth-child(5),td:nth-child(5) {{ display:none; }} }}
</style>
</head>
<body>
<header class="header">
  <div class="header-inner">
    <div>
      <h1>本科专业市场观察总览</h1>
      <div class="sub">数据源：data/processed/rysxai · 最新抓取：{latest}</div>
    </div>
    <div class="controls">
      <input id="search" placeholder="搜索专业名称、代码、门类、专业类" />
      <select id="category"><option value="">全部门类</option></select>
      <select id="sort">
        <option value="code">按专业代码</option>
        <option value="heat">按热度</option>
        <option value="salary">按全国薪资</option>
        <option value="demand">按全国需求</option>
      </select>
    </div>
  </div>
</header>
<main class="main">
  <section id="stats" class="stats"></section>
  <section id="charts" class="charts"></section>
  <section class="grid">
    <div class="panel">
      <div class="head"><div class="title">专业列表</div><div id="resultCount" class="note"></div></div>
      <div class="table-wrap"><table><thead><tr><th>代码</th><th>专业</th><th>门类</th><th>专业类</th><th>全国薪资</th><th>全国需求</th></tr></thead><tbody id="tbody"></tbody></table></div>
    </div>
    <aside class="panel">
      <div class="head"><div class="title">专业详情</div><div class="note"><a id="reportLink" href="#">单专业报告</a></div></div>
      <div id="detail" class="detail"></div>
    </aside>
  </section>
</main>
<script id="payload" type="application/json">{payload_json}</script>
<script>
const payload = JSON.parse(document.getElementById('payload').textContent);
const records = payload.records;
let activeId = records[0] && records[0].id;
const fmt = new Intl.NumberFormat('zh-CN');
const byId = id => document.getElementById(id);
const money = n => Number.isFinite(Number(n)) ? fmt.format(Number(n)) : '-';
const pct = n => Number.isFinite(Number(n)) ? Number(n).toFixed(1) + '%' : '-';
function stat(label,value) {{ return '<div class="stat"><div class="label">'+label+'</div><div class="value">'+value+'</div></div>'; }}
function renderStats() {{
  const s = payload.summary;
  byId('stats').innerHTML = [
    stat('本科专业', fmt.format(s.total)),
    stat('学科门类', fmt.format(s.categoryCount)),
    stat('专业类', fmt.format(s.subjectCount)),
    stat('薪资覆盖', fmt.format(s.salaryCoverage) + '/' + fmt.format(s.total)),
    stat('全国薪资中位数', money(s.medianSalary)),
    stat('全国需求均值', money(s.avgDemand))
  ].join('');
}}
function bars(title, rows, color) {{
  const max = Math.max.apply(null, rows.map(x => x[1]).concat([1]));
  byId('charts').insertAdjacentHTML('beforeend', '<div class="chart"><h3>'+title+'</h3>' + rows.map(([label,value]) =>
    '<div class="bar"><div title="'+label+'">'+label+'</div><div class="track"><div class="fill '+(color||'')+'" style="width:'+Math.max(3,value/max*100)+'%"></div></div><div>'+fmt.format(value)+'</div></div>'
  ).join('') + '</div>');
}}
function filtered() {{
  const q = byId('search').value.trim().toLowerCase();
  const cat = byId('category').value;
  const sort = byId('sort').value;
  const list = records.filter(r => (!cat || r.category === cat) && (!q || [r.name,r.code,r.category,r.subject,r.degree].join(' ').toLowerCase().includes(q)));
  return list.sort((a,b) => {{
    if (sort === 'heat') return (b.heat || 0) - (a.heat || 0);
    if (sort === 'salary') return (b.nationalSalary || 0) - (a.nationalSalary || 0);
    if (sort === 'demand') return (b.nationalDemand || 0) - (a.nationalDemand || 0);
    return String(a.code).localeCompare(String(b.code), 'zh-CN');
  }});
}}
function renderTable() {{
  const list = filtered();
  byId('resultCount').textContent = fmt.format(list.length) + ' 个结果';
  byId('tbody').innerHTML = list.map(r =>
    '<tr data-id="'+r.id+'" class="'+(r.id === activeId ? 'active' : '')+'"><td class="code">'+r.code+'</td><td><strong>'+r.name+'</strong><div class="note">'+(r.degree || '-')+'</div></td><td><span class="badge">'+(r.category || '未分类')+'</span></td><td>'+(r.subject || '-')+'</td><td>'+money(r.nationalSalary)+'</td><td>'+money(r.nationalDemand)+'</td></tr>'
  ).join('') || '<tr><td colspan="6"><div class="empty">没有匹配结果</div></td></tr>';
  document.querySelectorAll('tr[data-id]').forEach(row => row.addEventListener('click', () => {{ activeId = Number(row.dataset.id); renderTable(); renderDetail(); }}));
  if (!list.some(r => r.id === activeId) && list[0]) {{ activeId = list[0].id; renderTable(); renderDetail(); }}
}}
function miniBars(items, valueKey, color) {{
  if (!items || !items.length) return '<div class="note">暂无数据</div>';
  const max = Math.max.apply(null, items.map(x => Number(x[valueKey]) || 0).concat([1]));
  return items.map(item => '<div class="bar"><div title="'+(item.label || item.region)+'">'+(item.label || item.region)+'</div><div class="track"><div class="fill '+(color||'')+'" style="width:'+Math.max(3,(Number(item[valueKey])||0)/max*100)+'%"></div></div><div>'+(valueKey === 'rate_percent' ? pct(item[valueKey]) : money(item[valueKey]))+'</div></div>').join('');
}}
function rank(rows, key, title) {{
  return '<div class="rank-card"><div class="section-title">'+title+'</div>' + ((rows || []).map(x => '<div class="rank-row"><span>'+x.region+'</span><strong>'+money(x[key])+'</strong></div>').join('') || '<div class="note">暂无数据</div>') + '</div>';
}}
function renderDetail() {{
  const r = records.find(x => x.id === activeId) || records[0];
  if (!r) return;
  byId('reportLink').href = r.report;
  byId('detail').innerHTML =
    '<h2>'+r.name+'</h2><div class="code">'+r.code+'</div><div class="meta"><span class="badge">'+(r.category || '未分类')+'</span><span class="badge green">'+(r.subject || '未分类')+'</span>'+(r.isHot ? '<span class="badge orange">热门</span>' : '')+'</div>' +
    '<div class="kv"><span>学位</span><strong>'+(r.degree || '-')+'</strong></div><div class="kv"><span>学制</span><strong>'+(r.limitYear || '-')+'</strong></div><div class="kv"><span>选科建议</span><strong>'+(r.selectionAdvice || '-')+'</strong></div><div class="kv"><span>样本量</span><strong>返回 '+money(r.jobSampleCount)+' / 声称 '+money(r.jobSampleReported)+'</strong></div>' +
    '<div class="section"><div class="section-title">行业分布</div>'+miniBars(r.topIndustries, 'rate_percent')+'</div>' +
    '<div class="section"><div class="section-title">地区分布</div>'+miniBars(r.topRegions, 'rate_percent', 'green')+'</div>' +
    '<div class="section"><div class="section-title">岗位方向</div>'+miniBars(r.topJobs, 'rate_percent')+'</div>' +
    '<div class="section rank-grid">'+rank(r.demandRanking, 'demand_count', '需求排行')+rank(r.salaryRanking, 'monthly_salary_reference', '薪资排行')+'</div>';
}}
function init() {{
  byId('category').innerHTML += payload.categories.map(c => '<option value="'+c+'">'+c+'</option>').join('');
  ['search','category','sort'].forEach(id => byId(id).addEventListener('input', renderTable));
  renderStats();
  bars('门类覆盖', payload.charts.categoryCounts.slice(0, 14));
  bars('高频就业行业', payload.charts.topIndustries.slice(0, 14), 'green');
  renderTable();
  renderDetail();
}}
init();
</script>
</body>
</html>
"""


def main():
    records = build_records()
    payload = build_payload(records)
    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUT_FILE.write_text(build_html(payload), encoding="utf-8")
    print(str(OUT_FILE))
    print(len(records))


if __name__ == "__main__":
    main()
