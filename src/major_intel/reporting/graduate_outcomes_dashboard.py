from __future__ import annotations

from collections import defaultdict
import csv
from datetime import date
import html
import json
from pathlib import Path
from typing import Any


DASHBOARD_RELATIVE_PATH = Path("outputs") / "graduate_outcomes" / "dashboard" / "index.html"
OUTPUT_DIR = Path("outputs") / "graduate_outcomes"
CLEAN_DIR = Path("data") / "cleaned" / "graduate_outcomes"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def read_manifest(root: Path) -> dict[str, Any]:
    manifest_path = root / OUTPUT_DIR / "package_manifest.json"
    return json.loads(manifest_path.read_text(encoding="utf-8"))


def to_int(value: str | int | None) -> int:
    if value is None or value == "":
        return 0
    return int(float(str(value).replace(",", "")))


def format_number(value: int | float) -> str:
    return f"{int(value):,}"


def is_true(value: str) -> bool:
    return value.strip().lower() == "true"


def shorten(text: str, limit: int = 170) -> str:
    text = " ".join((text or "").split())
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "..."


def sum_by(rows: list[dict[str, str]], key: str, value_key: str = "record_count") -> list[dict[str, Any]]:
    totals: dict[str, int] = defaultdict(int)
    for row in rows:
        label = row.get(key) or "未标注"
        totals[label] += to_int(row.get(value_key))
    return [
        {"label": label, "value": value}
        for label, value in sorted(totals.items(), key=lambda item: item[1], reverse=True)
    ]


def count_by(rows: list[dict[str, str]], key: str) -> list[dict[str, Any]]:
    totals: dict[str, int] = defaultdict(int)
    for row in rows:
        label = row.get(key) or "未标注"
        totals[label] += 1
    return [
        {"label": label, "value": value}
        for label, value in sorted(totals.items(), key=lambda item: item[1], reverse=True)
    ]


def sum_by_year(rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    totals: dict[str, int] = defaultdict(int)
    for row in rows:
        year = row.get("year") or "未标注"
        totals[year] += to_int(row.get("record_count"))
    return [{"year": year, "records": totals[year]} for year in sorted(totals)]


def top_schools_from_source_summary(rows: list[dict[str, str]], limit: int = 30) -> list[dict[str, Any]]:
    records: dict[str, int] = defaultdict(int)
    documents: dict[str, int] = defaultdict(int)
    years: dict[str, set[str]] = defaultdict(set)
    datasets: dict[str, set[str]] = defaultdict(set)
    for row in rows:
        school = row.get("school_name") or "未标注"
        records[school] += to_int(row.get("record_count"))
        documents[school] += to_int(row.get("source_document_count"))
        if row.get("year"):
            years[school].add(row["year"])
        if row.get("source_dataset"):
            datasets[school].add(row["source_dataset"])
    return [
        {
            "school_name": school,
            "records": count,
            "source_documents": documents[school],
            "years": ", ".join(sorted(years[school])),
            "source_datasets": ", ".join(sorted(datasets[school])),
        }
        for school, count in sorted(records.items(), key=lambda item: item[1], reverse=True)[:limit]
    ]


def top_undergraduate_sources(rows: list[dict[str, str]], limit: int = 30) -> list[dict[str, Any]]:
    records: dict[str, int] = defaultdict(int)
    destinations: dict[str, set[str]] = defaultdict(set)
    years: dict[str, set[str]] = defaultdict(set)
    for row in rows:
        school = row.get("undergraduate_school") or "未标注"
        records[school] += to_int(row.get("record_count"))
        if row.get("destination_school"):
            destinations[school].add(row["destination_school"])
        if row.get("year"):
            years[school].add(row["year"])
    return [
        {
            "undergraduate_school": school,
            "records": count,
            "destination_count": len(destinations[school]),
            "years": ", ".join(sorted(years[school])),
        }
        for school, count in sorted(records.items(), key=lambda item: item[1], reverse=True)[:limit]
    ]


def coverage_by_province(rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    provinces: dict[str, dict[str, int]] = defaultdict(lambda: {"total": 0, "covered": 0, "records": 0})
    for row in rows:
        province = row.get("province") or "未标注"
        item = provinces[province]
        item["total"] += 1
        if is_true(row.get("has_official_recommendation_records", "")):
            item["covered"] += 1
        item["records"] += to_int(row.get("official_recommendation_record_count"))
    results: list[dict[str, Any]] = []
    for province, values in provinces.items():
        total = values["total"]
        covered = values["covered"]
        results.append(
            {
                "province": province,
                "total": total,
                "covered": covered,
                "uncovered": total - covered,
                "records": values["records"],
                "coverage_rate": covered / total if total else 0,
            }
        )
    return sorted(results, key=lambda row: (-row["uncovered"], -row["records"], row["province"]))


def blocker_rows(
    coverage_rows: list[dict[str, str]],
    remaining_rows: list[dict[str, str]],
    recheck_rows: list[dict[str, str]],
) -> list[dict[str, Any]]:
    remaining_by_school = {row.get("school_name", ""): row for row in remaining_rows}
    recheck_by_school = {row.get("school_name", ""): row for row in recheck_rows}
    blockers: list[dict[str, Any]] = []
    for row in coverage_rows:
        if is_true(row.get("has_official_recommendation_records", "")):
            continue
        school = row.get("school_name", "")
        remaining = remaining_by_school.get(school, {})
        recheck = recheck_by_school.get(school, {})
        urls = (
            remaining.get("official_candidate_urls")
            or recheck.get("official_evidence_urls")
            or row.get("official_url")
            or ""
        )
        evidence_urls = [url.strip() for url in urls.replace(";", "|").split("|") if url.strip()]
        notes = remaining.get("current_status") or recheck.get("recheck_result") or row.get("coverage_note", "")
        blockers.append(
            {
                "school_name": school,
                "province": row.get("province", ""),
                "blocker_type": remaining.get("blocker_type") or "public_source_unavailable",
                "status": shorten(notes, 220),
                "unblock_requirement": remaining.get("unblock_requirement")
                or "需要可公开访问的官方最终名单正文或附件",
                "evidence_url_count": len(evidence_urls),
                "sample_urls": evidence_urls[:3],
            }
        )
    return sorted(blockers, key=lambda item: item["school_name"])


def build_dashboard_data(root: Path) -> dict[str, Any]:
    manifest = read_manifest(root)
    source_summary = read_csv(root / CLEAN_DIR / "school_year_source_summary.csv")
    undergrad_summary = read_csv(root / CLEAN_DIR / "undergraduate_school_outcome_summary.csv")
    coverage = read_csv(root / CLEAN_DIR / "official_recommendation_school_coverage.csv")
    remaining = read_csv(root / OUTPUT_DIR / "remaining_uncovered_schools.csv")
    recheck = read_csv(root / OUTPUT_DIR / "remaining_uncovered_recheck_2026-06-04.csv")
    employment_metrics = read_csv(root / CLEAN_DIR / "official_employment_report_metrics.csv")

    target_schools = int(manifest["coverage"]["target_schools"])
    covered_schools = sum(1 for row in coverage if is_true(row.get("has_official_recommendation_records", "")))
    uncovered_schools = target_schools - covered_schools
    public_records = int(manifest["csv_row_counts"]["master_records_public.csv"])
    source_document_count = sum(to_int(row.get("source_document_count")) for row in source_summary)

    blockers = blocker_rows(coverage, remaining, recheck)
    data = {
        "generated_at": manifest.get("generated_at") or str(date.today()),
        "status": manifest.get("status", ""),
        "metrics": {
            "target_schools": target_schools,
            "covered_schools": covered_schools,
            "uncovered_schools": uncovered_schools,
            "public_records": public_records,
            "coverage_rate": covered_schools / target_schools if target_schools else 0,
            "source_summary_rows": len(source_summary),
            "undergrad_summary_rows": len(undergrad_summary),
            "employment_metric_rows": len(employment_metrics),
            "source_document_count": source_document_count,
        },
        "charts": {
            "records_by_year": sum_by_year(source_summary),
            "records_by_source": sum_by(source_summary, "source_dataset"),
            "records_by_document_type": sum_by(source_summary, "document_type"),
            "records_by_route": sum_by(source_summary, "route"),
            "employment_metrics_by_name": count_by(employment_metrics, "metric_name"),
            "top_destination_schools": top_schools_from_source_summary(source_summary),
            "top_undergraduate_schools": top_undergraduate_sources(undergrad_summary),
        },
        "tables": {
            "coverage_by_province": coverage_by_province(coverage),
            "blockers": blockers,
            "top_destination_schools": top_schools_from_source_summary(source_summary, 80),
            "top_undergraduate_schools": top_undergraduate_sources(undergrad_summary, 80),
        },
        "sources": [
            {
                "label": "package_manifest.json",
                "path": "outputs/graduate_outcomes/package_manifest.json",
                "rows": None,
            },
            {
                "label": "Source_Summary",
                "path": "data/cleaned/graduate_outcomes/school_year_source_summary.csv",
                "rows": len(source_summary),
            },
            {
                "label": "Coverage",
                "path": "data/cleaned/graduate_outcomes/official_recommendation_school_coverage.csv",
                "rows": len(coverage),
            },
            {
                "label": "Undergrad_Source_Outcomes",
                "path": "data/cleaned/graduate_outcomes/undergraduate_school_outcome_summary.csv",
                "rows": len(undergrad_summary),
            },
            {
                "label": "Remaining_Uncovered_Recheck",
                "path": "outputs/graduate_outcomes/remaining_uncovered_recheck_2026-06-04.csv",
                "rows": len(recheck),
            },
            {
                "label": "Employment_Metrics",
                "path": "data/cleaned/graduate_outcomes/official_employment_report_metrics.csv",
                "rows": len(employment_metrics),
            },
        ],
    }
    return data


CSS = r"""
:root {
  --bg: #f7f9fb;
  --surface: #ffffff;
  --surface-2: #f1f5f9;
  --text: #14213d;
  --muted: #64748b;
  --border: #d9e2ec;
  --teal: #0f766e;
  --blue: #2563eb;
  --amber: #b7791f;
  --rose: #be123c;
  --slate: #334155;
  --shadow: 0 18px 45px rgba(15, 23, 42, 0.08);
}

* { box-sizing: border-box; }
html { scroll-behavior: smooth; }
body {
  margin: 0;
  min-width: 320px;
  background: var(--bg);
  color: var(--text);
  font-family: "Microsoft YaHei", "PingFang SC", "Noto Sans CJK SC", "Segoe UI", Arial, sans-serif;
  letter-spacing: 0;
}
a { color: var(--blue); text-decoration: none; }
a:hover { text-decoration: underline; }
.app-shell { width: min(1440px, calc(100% - 32px)); margin: 0 auto; padding: 24px 0 40px; }
.topbar {
  display: flex;
  justify-content: space-between;
  gap: 20px;
  align-items: flex-start;
  padding: 4px 0 18px;
}
.title-stack h1 { margin: 0; font-size: 28px; line-height: 1.2; font-weight: 760; }
.title-stack p { margin: 8px 0 0; color: var(--muted); font-size: 13px; line-height: 1.6; max-width: 860px; }
.top-actions { display: flex; flex-wrap: wrap; justify-content: flex-end; gap: 8px; }
.button {
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--surface);
  color: var(--slate);
  min-height: 36px;
  padding: 8px 12px;
  font-size: 13px;
  font-weight: 650;
  display: inline-flex;
  align-items: center;
  gap: 7px;
  box-shadow: 0 1px 2px rgba(15, 23, 42, 0.05);
}
.button.primary { background: #0f766e; color: #fff; border-color: #0f766e; }
.status-band {
  display: grid;
  grid-template-columns: minmax(280px, 1.45fr) minmax(260px, 1fr);
  gap: 16px;
  margin-bottom: 16px;
  align-items: start;
}
.panel, .kpi-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 8px;
  box-shadow: var(--shadow);
}
.panel { padding: 18px; }
.status-band > .panel:last-child {
  max-height: 314px;
  overflow: auto;
}
.status-copy { display: grid; grid-template-columns: auto 1fr; gap: 18px; align-items: center; }
.status-copy > * { min-width: 0; }
.coverage-ring { width: 152px; height: 152px; position: relative; display: grid; place-items: center; }
.coverage-ring svg { position: absolute; inset: 0; width: 152px; height: 152px; transform: rotate(-90deg); }
.coverage-ring .ring-value { font-size: 30px; font-weight: 780; line-height: 1; }
.coverage-ring .ring-label { margin-top: 6px; font-size: 12px; color: var(--muted); text-align: center; }
.status-text h2 { margin: 0; font-size: 18px; line-height: 1.3; }
.status-text p { margin: 8px 0 0; color: var(--muted); font-size: 13px; line-height: 1.65; }
.status-text h2, .status-text p, .blocker-status, .kpi-note { overflow-wrap: anywhere; }
.status-legend { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 12px; }
.tag {
  display: inline-flex;
  align-items: center;
  min-height: 26px;
  padding: 4px 8px;
  border: 1px solid var(--border);
  border-radius: 8px;
  font-size: 12px;
  color: var(--slate);
  background: var(--surface-2);
}
.tag.warn { color: #92400e; background: #fff7ed; border-color: #fed7aa; }
.kpi-grid { display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 12px; margin-bottom: 16px; }
.kpi-card { padding: 14px 14px 13px; min-height: 96px; }
.kpi-label { font-size: 12px; color: var(--muted); margin-bottom: 10px; }
.kpi-value { font-size: 27px; font-weight: 780; line-height: 1.05; }
.kpi-note { font-size: 12px; color: var(--muted); margin-top: 8px; line-height: 1.35; }
.tabs {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  border-bottom: 1px solid var(--border);
  margin-bottom: 16px;
}
.tab-button {
  border: 0;
  border-radius: 8px 8px 0 0;
  background: transparent;
  color: var(--muted);
  padding: 11px 13px;
  font-weight: 700;
  font-size: 13px;
  cursor: pointer;
}
.tab-button.active { background: var(--surface); color: var(--teal); border: 1px solid var(--border); border-bottom-color: var(--surface); margin-bottom: -1px; }
.tab-panel { display: none; }
.tab-panel.active { display: block; }
.grid-2 { display: grid; grid-template-columns: minmax(0, 1.15fr) minmax(320px, 0.85fr); gap: 16px; }
.grid-3 { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 16px; }
.grid-2 > *, .grid-3 > *, .method-grid > *, .status-band > * { min-width: 0; }
.section-title { display: flex; justify-content: space-between; gap: 12px; align-items: baseline; margin-bottom: 12px; }
.section-title h3 { margin: 0; font-size: 16px; line-height: 1.3; }
.section-title span { color: var(--muted); font-size: 12px; }
.chart-box { min-height: 288px; }
.chart-box svg { width: 100%; height: auto; display: block; overflow: visible; }
.axis-label, .chart-label { fill: #64748b; font-size: 12px; }
.chart-value { fill: #14213d; font-size: 12px; font-weight: 700; }
.blocker-list { display: grid; gap: 10px; }
.blocker-item {
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 12px;
  background: #fff;
}
.blocker-head { display: flex; justify-content: space-between; gap: 10px; align-items: center; margin-bottom: 8px; }
.blocker-name { font-weight: 750; font-size: 14px; }
.blocker-type { font-size: 12px; color: var(--rose); font-weight: 700; }
.blocker-status { color: var(--muted); font-size: 12px; line-height: 1.55; margin: 0; }
.control-row { display: flex; flex-wrap: wrap; gap: 10px; margin-bottom: 12px; align-items: center; }
.input, .select {
  height: 36px;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--surface);
  color: var(--text);
  padding: 0 10px;
  font-size: 13px;
  min-width: 180px;
}
.table-wrap {
  overflow: auto;
  width: 100%;
  max-width: 100%;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--surface);
}
table { width: 100%; border-collapse: collapse; min-width: 760px; }
th, td { padding: 10px 12px; border-bottom: 1px solid #e8eef5; text-align: left; font-size: 12px; line-height: 1.45; white-space: nowrap; }
th { position: sticky; top: 0; background: #f8fafc; color: var(--slate); z-index: 1; font-size: 12px; }
td.numeric, th.numeric { text-align: right; }
tbody tr:hover { background: #f8fafc; }
.method-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 16px; }
.source-list { display: grid; gap: 8px; }
.source-item { display: flex; justify-content: space-between; gap: 12px; border-bottom: 1px solid #e8eef5; padding-bottom: 8px; font-size: 12px; }
.source-path { color: var(--muted); overflow-wrap: anywhere; }
.empty { color: var(--muted); padding: 16px; font-size: 13px; }

@media (max-width: 980px) {
  .app-shell { width: min(100% - 20px, 900px); padding-top: 16px; }
  .topbar, .status-band, .grid-2, .grid-3, .method-grid { grid-template-columns: 1fr; display: grid; }
  .top-actions { justify-content: flex-start; }
  .kpi-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}

@media (max-width: 620px) {
  .title-stack h1 { font-size: 22px; }
  .status-copy { grid-template-columns: 1fr; justify-items: start; }
  .kpi-grid { grid-template-columns: 1fr; }
  .panel { padding: 14px; }
  .input, .select { min-width: 100%; width: 100%; }
  .control-row { align-items: stretch; }
  th, td { padding: 9px 10px; }
}
"""


JS = r"""
const dataNode = document.getElementById("dashboard-data");
const dashboardData = JSON.parse(dataNode.textContent);
const metrics = dashboardData.metrics;

const formatNumber = (value) => Number(value || 0).toLocaleString("zh-CN");
const formatPercent = (value) => `${(Number(value || 0) * 100).toFixed(1)}%`;

function setText(id, value) {
  const el = document.getElementById(id);
  if (el) el.textContent = value;
}

function initKpis() {
  setText("kpi-target", formatNumber(metrics.target_schools));
  setText("kpi-covered", formatNumber(metrics.covered_schools));
  setText("kpi-rate", formatPercent(metrics.coverage_rate));
  setText("kpi-records", formatNumber(metrics.public_records));
  setText("kpi-blockers", formatNumber(metrics.uncovered_schools));
  setText("source-documents", formatNumber(metrics.source_document_count));
}

function initTabs() {
  document.querySelectorAll(".tab-button").forEach((button) => {
    button.addEventListener("click", () => {
      const tab = button.dataset.tab;
      document.querySelectorAll(".tab-button").forEach((item) => item.classList.toggle("active", item === button));
      document.querySelectorAll(".tab-panel").forEach((panel) => panel.classList.toggle("active", panel.id === tab));
    });
  });
}

function renderCoverageRing() {
  const el = document.getElementById("coverage-ring");
  const radius = 61;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference * (1 - metrics.coverage_rate);
  el.innerHTML = `
    <svg viewBox="0 0 152 152" aria-hidden="true">
      <circle cx="76" cy="76" r="${radius}" fill="none" stroke="#e2e8f0" stroke-width="14"></circle>
      <circle cx="76" cy="76" r="${radius}" fill="none" stroke="#0f766e" stroke-linecap="round" stroke-width="14"
        stroke-dasharray="${circumference}" stroke-dashoffset="${offset}"></circle>
    </svg>
    <div>
      <div class="ring-value">${formatPercent(metrics.coverage_rate)}</div>
      <div class="ring-label">${formatNumber(metrics.covered_schools)} / ${formatNumber(metrics.target_schools)}</div>
    </div>`;
}

function barChart(targetId, rows, options = {}) {
  const el = document.getElementById(targetId);
  const width = 760;
  const height = options.height || 278;
  const margin = { top: 18, right: 24, bottom: 46, left: 58 };
  const chartWidth = width - margin.left - margin.right;
  const chartHeight = height - margin.top - margin.bottom;
  const maxValue = Math.max(...rows.map((row) => Number(row[options.valueKey] || row.value || row.records || 0)), 1);
  const barGap = 8;
  const barWidth = chartWidth / rows.length - barGap;
  const color = options.color || "#2563eb";
  const bars = rows.map((row, index) => {
    const value = Number(row[options.valueKey] || row.value || row.records || 0);
    const label = row[options.labelKey] || row.label || row.year;
    const x = margin.left + index * (chartWidth / rows.length) + barGap / 2;
    const barHeight = value / maxValue * chartHeight;
    const y = margin.top + chartHeight - barHeight;
    return `
      <rect x="${x}" y="${y}" width="${Math.max(barWidth, 8)}" height="${barHeight}" rx="4" fill="${color}">
        <title>${label}: ${formatNumber(value)}</title>
      </rect>
      <text x="${x + Math.max(barWidth, 8) / 2}" y="${height - 18}" text-anchor="middle" class="axis-label">${label}</text>
    `;
  }).join("");
  el.innerHTML = `
    <svg viewBox="0 0 ${width} ${height}" role="img" aria-label="${options.title || "bar chart"}">
      <line x1="${margin.left}" y1="${margin.top + chartHeight}" x2="${width - margin.right}" y2="${margin.top + chartHeight}" stroke="#d9e2ec"></line>
      ${bars}
    </svg>`;
}

function horizontalBars(targetId, rows, options = {}) {
  const el = document.getElementById(targetId);
  const selected = rows.slice(0, options.limit || 12);
  const width = 760;
  const rowHeight = 28;
  const margin = { top: 8, right: 90, bottom: 16, left: options.left || 170 };
  const height = margin.top + margin.bottom + selected.length * rowHeight;
  const maxValue = Math.max(...selected.map((row) => Number(row[options.valueKey] || row.value || row.records || 0)), 1);
  const chartWidth = width - margin.left - margin.right;
  const color = options.color || "#0f766e";
  const bars = selected.map((row, index) => {
    const label = row[options.labelKey] || row.label || row.school_name || row.undergraduate_school;
    const value = Number(row[options.valueKey] || row.value || row.records || 0);
    const y = margin.top + index * rowHeight;
    const barWidth = value / maxValue * chartWidth;
    return `
      <text x="${margin.left - 10}" y="${y + 18}" text-anchor="end" class="chart-label">${escapeSvg(label)}</text>
      <rect x="${margin.left}" y="${y + 5}" width="${barWidth}" height="16" rx="4" fill="${color}">
        <title>${escapeSvg(label)}: ${formatNumber(value)}</title>
      </rect>
      <text x="${margin.left + barWidth + 8}" y="${y + 18}" class="chart-value">${formatNumber(value)}</text>
    `;
  }).join("");
  el.innerHTML = `<svg viewBox="0 0 ${width} ${height}" role="img" aria-label="${options.title || "horizontal bar chart"}">${bars}</svg>`;
}

function escapeSvg(value) {
  return String(value ?? "").replace(/[&<>"']/g, (char) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    "\"": "&quot;",
    "'": "&#39;"
  }[char]));
}

function renderBlockers() {
  const el = document.getElementById("blocker-list");
  el.innerHTML = dashboardData.tables.blockers.map((row) => `
    <article class="blocker-item">
      <div class="blocker-head">
        <span class="blocker-name">${escapeHtml(row.school_name)}</span>
        <span class="blocker-type">${escapeHtml(row.blocker_type)}</span>
      </div>
      <p class="blocker-status">${escapeHtml(row.status)}</p>
    </article>
  `).join("");
}

function escapeHtml(value) {
  return String(value ?? "").replace(/[&<>"']/g, (char) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    "\"": "&quot;",
    "'": "&#39;"
  }[char]));
}

function renderTable(targetId, rows, columns) {
  const el = document.getElementById(targetId);
  if (!rows.length) {
    el.innerHTML = '<div class="empty">没有匹配数据</div>';
    return;
  }
  const head = columns.map((col) => `<th class="${col.numeric ? "numeric" : ""}">${escapeHtml(col.label)}</th>`).join("");
  const body = rows.map((row) => {
    const cells = columns.map((col) => {
      let value = row[col.key];
      if (col.percent) value = formatPercent(value);
      if (col.number) value = formatNumber(value);
      return `<td class="${col.numeric ? "numeric" : ""}">${escapeHtml(value)}</td>`;
    }).join("");
    return `<tr>${cells}</tr>`;
  }).join("");
  el.innerHTML = `<table><thead><tr>${head}</tr></thead><tbody>${body}</tbody></table>`;
}

function initTables() {
  renderTable("province-table", dashboardData.tables.coverage_by_province, [
    { key: "province", label: "省份" },
    { key: "covered", label: "已覆盖", number: true, numeric: true },
    { key: "total", label: "目标", number: true, numeric: true },
    { key: "uncovered", label: "待补", number: true, numeric: true },
    { key: "coverage_rate", label: "覆盖率", percent: true, numeric: true },
    { key: "records", label: "记录数", number: true, numeric: true },
  ]);

  renderTable("blocker-table", dashboardData.tables.blockers, [
    { key: "school_name", label: "院校" },
    { key: "province", label: "省份" },
    { key: "blocker_type", label: "阻塞类型" },
    { key: "evidence_url_count", label: "证据 URL", number: true, numeric: true },
    { key: "unblock_requirement", label: "补齐条件" },
  ]);

  renderSchoolTables();
}

function renderSchoolTables() {
  const query = document.getElementById("school-search").value.trim().toLowerCase();
  const destinationRows = dashboardData.tables.top_destination_schools
    .filter((row) => !query || row.school_name.toLowerCase().includes(query))
    .slice(0, 40);
  const undergradRows = dashboardData.tables.top_undergraduate_schools
    .filter((row) => !query || row.undergraduate_school.toLowerCase().includes(query))
    .slice(0, 40);

  renderTable("destination-table", destinationRows, [
    { key: "school_name", label: "目标院校" },
    { key: "records", label: "记录数", number: true, numeric: true },
    { key: "source_documents", label: "文档数", number: true, numeric: true },
    { key: "years", label: "年份" },
    { key: "source_datasets", label: "来源" },
  ]);

  renderTable("undergrad-table", undergradRows, [
    { key: "undergraduate_school", label: "本科来源院校" },
    { key: "records", label: "记录数", number: true, numeric: true },
    { key: "destination_count", label: "去向院校数", number: true, numeric: true },
    { key: "years", label: "年份" },
  ]);
}

function initControls() {
  document.getElementById("school-search").addEventListener("input", renderSchoolTables);
  document.getElementById("topn").addEventListener("change", () => {
    const limit = Number(document.getElementById("topn").value);
    horizontalBars("top-destinations-chart", dashboardData.charts.top_destination_schools, {
      labelKey: "school_name", valueKey: "records", limit, color: "#0f766e", left: 190
    });
    horizontalBars("top-undergrad-chart", dashboardData.charts.top_undergraduate_schools, {
      labelKey: "undergraduate_school", valueKey: "records", limit, color: "#b7791f", left: 190
    });
  });
}

function initCharts() {
  barChart("records-year-chart", dashboardData.charts.records_by_year, {
    labelKey: "year", valueKey: "records", color: "#2563eb", title: "records by year"
  });
  horizontalBars("source-chart", dashboardData.charts.records_by_source, {
    labelKey: "label", valueKey: "value", limit: 8, color: "#0f766e", left: 230
  });
  horizontalBars("document-type-chart", dashboardData.charts.records_by_document_type, {
    labelKey: "label", valueKey: "value", limit: 8, color: "#2563eb", left: 250
  });
  horizontalBars("route-chart", dashboardData.charts.records_by_route, {
    labelKey: "label", valueKey: "value", limit: 8, color: "#b7791f", left: 250
  });
  horizontalBars("top-destinations-chart", dashboardData.charts.top_destination_schools, {
    labelKey: "school_name", valueKey: "records", limit: 12, color: "#0f766e", left: 190
  });
  horizontalBars("top-undergrad-chart", dashboardData.charts.top_undergraduate_schools, {
    labelKey: "undergraduate_school", valueKey: "records", limit: 12, color: "#b7791f", left: 190
  });
}

function initSources() {
  const el = document.getElementById("source-list");
  el.innerHTML = dashboardData.sources.map((source) => `
    <div class="source-item">
      <div>
        <strong>${escapeHtml(source.label)}</strong>
        <div class="source-path">${escapeHtml(source.path)}</div>
      </div>
      <span>${source.rows === null ? "manifest" : `${formatNumber(source.rows)} 行`}</span>
    </div>
  `).join("");
}

initKpis();
initTabs();
initControls();
renderCoverageRing();
renderBlockers();
initCharts();
initTables();
initSources();
"""


def render_html(data: dict[str, Any]) -> str:
    metrics = data["metrics"]
    data_json = html.escape(json.dumps(data, ensure_ascii=False, separators=(",", ":")), quote=False)
    generated_at = html.escape(data["generated_at"])
    status = html.escape(data["status"])
    coverage_percent = f"{metrics['coverage_rate'] * 100:.1f}%"
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>研究生去向数据看板</title>
  <link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='6' fill='%230f766e'/%3E%3Cpath d='M8 22h16v2H8zm2-4h3V9h-3zm5 0h3V6h-3zm5 0h3v-7h-3z' fill='white'/%3E%3C/svg%3E">
  <style>{CSS}</style>
</head>
<body>
  <main class="app-shell">
    <header class="topbar">
      <div class="title-stack">
        <h1>研究生去向数据看板</h1>
        <p>当前包生成日期 {generated_at}。覆盖口径为公开、官方、最终行级推荐/录取名单；未满足该口径的辅助材料不计入覆盖。</p>
      </div>
      <div class="top-actions" aria-label="导出与来源">
        <a class="button primary" href="../graduate_outcomes_clean_data_package.xlsx">下载工作簿</a>
        <a class="button" href="../README.md">查看 README</a>
      </div>
    </header>

    <section class="status-band" aria-label="状态总览">
      <div class="panel status-copy">
        <div id="coverage-ring" class="coverage-ring" aria-label="覆盖率 {coverage_percent}"></div>
        <div class="status-text">
          <h2>425 / 430 所院校已有可计入官方最终行级数据</h2>
          <p>状态：{status}。剩余 5 所主要受 JS challenge、WAF、公开页面无最终行级名单或文档类型不符影响。</p>
          <div class="status-legend">
            <span class="tag">公共记录 {format_number(metrics["public_records"])} 条</span>
            <span class="tag">来源摘要 {format_number(metrics["source_summary_rows"])} 行</span>
            <span class="tag warn">待补院校 {format_number(metrics["uncovered_schools"])} 所</span>
          </div>
        </div>
      </div>
      <div class="panel">
        <div class="section-title">
          <h3>当前阻塞项</h3>
          <span>只列未计入覆盖的院校</span>
        </div>
        <div id="blocker-list" class="blocker-list"></div>
      </div>
    </section>

    <section class="kpi-grid" aria-label="核心指标">
      <div class="kpi-card"><div class="kpi-label">目标院校</div><div id="kpi-target" class="kpi-value">{format_number(metrics["target_schools"])}</div><div class="kpi-note">固定院校池</div></div>
      <div class="kpi-card"><div class="kpi-label">已覆盖</div><div id="kpi-covered" class="kpi-value">{format_number(metrics["covered_schools"])}</div><div class="kpi-note">官方最终行级</div></div>
      <div class="kpi-card"><div class="kpi-label">覆盖率</div><div id="kpi-rate" class="kpi-value">{coverage_percent}</div><div class="kpi-note">425 / 430</div></div>
      <div class="kpi-card"><div class="kpi-label">公共记录</div><div id="kpi-records" class="kpi-value">{format_number(metrics["public_records"])}</div><div class="kpi-note">浏览器展示聚合数据</div></div>
      <div class="kpi-card"><div class="kpi-label">待补院校</div><div id="kpi-blockers" class="kpi-value">{format_number(metrics["uncovered_schools"])}</div><div class="kpi-note">需官方可访问正文/附件</div></div>
    </section>

    <nav class="tabs" aria-label="看板视图">
      <button class="tab-button active" data-tab="overview" type="button">总览</button>
      <button class="tab-button" data-tab="coverage" type="button">覆盖</button>
      <button class="tab-button" data-tab="sources" type="button">来源</button>
      <button class="tab-button" data-tab="schools" type="button">院校</button>
      <button class="tab-button" data-tab="blockers" type="button">阻塞项</button>
      <button class="tab-button" data-tab="methodology" type="button">口径</button>
    </nav>

    <section id="overview" class="tab-panel active">
      <div class="grid-2">
        <div class="panel">
          <div class="section-title"><h3>年度记录量</h3><span>Source_Summary 汇总</span></div>
          <div id="records-year-chart" class="chart-box"></div>
        </div>
        <div class="panel">
          <div class="section-title"><h3>来源数据集构成</h3><span>按 record_count</span></div>
          <div id="source-chart" class="chart-box"></div>
        </div>
      </div>
    </section>

    <section id="coverage" class="tab-panel">
      <div class="panel">
        <div class="section-title"><h3>省份覆盖明细</h3><span>覆盖率、待补数量和记录量</span></div>
        <div id="province-table" class="table-wrap"></div>
      </div>
    </section>

    <section id="sources" class="tab-panel">
      <div class="grid-3">
        <div class="panel">
          <div class="section-title"><h3>文档类型</h3><span>按 record_count</span></div>
          <div id="document-type-chart" class="chart-box"></div>
        </div>
        <div class="panel">
          <div class="section-title"><h3>数据路线</h3><span>按 route</span></div>
          <div id="route-chart" class="chart-box"></div>
        </div>
        <div class="panel">
          <div class="section-title"><h3>源文件</h3><span>聚合输入</span></div>
          <div id="source-list" class="source-list"></div>
        </div>
      </div>
    </section>

    <section id="schools" class="tab-panel">
      <div class="control-row">
        <input id="school-search" class="input" type="search" placeholder="搜索院校名称">
        <select id="topn" class="select" aria-label="排行数量">
          <option value="12">Top 12</option>
          <option value="20">Top 20</option>
          <option value="30">Top 30</option>
        </select>
      </div>
      <div class="grid-2">
        <div class="panel">
          <div class="section-title"><h3>目标院校记录排行</h3><span>按记录数</span></div>
          <div id="top-destinations-chart" class="chart-box"></div>
          <div id="destination-table" class="table-wrap"></div>
        </div>
        <div class="panel">
          <div class="section-title"><h3>本科来源院校排行</h3><span>按记录数</span></div>
          <div id="top-undergrad-chart" class="chart-box"></div>
          <div id="undergrad-table" class="table-wrap"></div>
        </div>
      </div>
    </section>

    <section id="blockers" class="tab-panel">
      <div class="panel">
        <div class="section-title"><h3>剩余未覆盖院校</h3><span>当前公开官方来源阻塞原因</span></div>
        <div id="blocker-table" class="table-wrap"></div>
      </div>
    </section>

    <section id="methodology" class="tab-panel">
      <div class="method-grid">
        <div class="panel">
          <div class="section-title"><h3>计入口径</h3><span>覆盖和记录口径</span></div>
          <p class="blocker-status">只统计公开可访问的官方最终行级推荐或录取名单正文、PDF、XLS、XLSX。候选编号、成绩表、调剂公告、搜索摘要、第三方镜像和需要登录或绕过防护的页面不计入覆盖。</p>
          <p class="blocker-status">页面内图表使用预聚合数据，核心明细仍以工作簿和 cleaned CSV 为准。源文档计数：<strong id="source-documents">{format_number(metrics["source_document_count"])}</strong>。</p>
        </div>
        <div class="panel">
          <div class="section-title"><h3>刷新方式</h3><span>可复现生成</span></div>
          <p class="blocker-status">运行 <code>python scripts/build_graduate_outcomes_dashboard.py</code> 可从当前本地数据重新生成本页面。</p>
          <p class="blocker-status">本页面不请求网络、不依赖外部 JavaScript 库、不加载 285,608 行明细到浏览器。</p>
        </div>
      </div>
    </section>
  </main>

  <script id="dashboard-data" type="application/json">{data_json}</script>
  <script>{JS}</script>
</body>
</html>
"""


def build_dashboard(root: Path, output_path: Path) -> dict[str, Any]:
    data = build_dashboard_data(root)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(render_html(data), encoding="utf-8", newline="\n")
    return data


def main() -> None:
    root = Path(__file__).resolve().parents[3]
    output_path = root / DASHBOARD_RELATIVE_PATH
    data = build_dashboard(root, output_path)
    metrics = data["metrics"]
    print(f"wrote {output_path}")
    print(
        "coverage "
        f"{metrics['covered_schools']}/{metrics['target_schools']} "
        f"({metrics['coverage_rate']:.1%}); "
        f"public_records={metrics['public_records']}"
    )


if __name__ == "__main__":
    main()
