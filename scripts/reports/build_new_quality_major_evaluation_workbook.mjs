import fs from "node:fs/promises";
import path from "node:path";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const inputPath = process.argv[2] ?? "outputs/new_quality_major_eval_20260613/new_quality_major_evaluation_workbook_data.json";
const outputPath = process.argv[3] ?? "outputs/new_quality_major_eval_20260613/new_quality_major_evaluation.xlsx";

const payload = JSON.parse(await fs.readFile(inputPath, "utf8"));
const workbook = Workbook.create();

const COLORS = {
  navy: "#1F4E78",
  blue: "#D9EAF7",
  paleBlue: "#EAF4FB",
  gray: "#F3F4F6",
  border: "#D7DEE8",
  yes: "#C6EFCE",
  related: "#DDEBF7",
  weak: "#FFF2CC",
  no: "#E7E6E6",
  review: "#FCE4D6",
};

const summaryFields = [
  ["major_special_id", "专业ID"],
  ["major_code", "专业代码"],
  ["major_name", "专业名称"],
  ["major_type", "专业层次"],
  ["major_level2", "门类/大类"],
  ["major_level3", "专业类"],
  ["evaluation_label", "定性标签"],
  ["is_new_quality_productivity_major", "是否新质生产力专业"],
  ["directions", "方向"],
  ["confidence", "置信度"],
  ["score", "规则分"],
  ["rationale", "判定理由"],
  ["policy_source_ids", "政策来源ID"],
  ["policy_evidence_excerpt", "政策证据摘录"],
  ["official_major_source", "专业来源"],
  ["qingbei_sample", "清北样本"],
  ["tier_985_sample", "985样本"],
  ["tier_211_sample", "211样本"],
  ["shuangfei_sample", "双非样本"],
  ["sample_coverage", "样本覆盖"],
  ["needs_review", "需复核"],
];

const detailFields = [
  ["major_special_id", "专业ID"],
  ["major_code", "专业代码"],
  ["major_name", "专业名称"],
  ["major_type", "专业层次"],
  ["major_level2", "门类/大类"],
  ["major_level3", "专业类"],
  ["school_tier", "院校层次"],
  ["sample_school_id", "样本院校ID"],
  ["sample_school_name", "样本院校"],
  ["sample_school_rank", "样本院校排名"],
  ["sample_school_found", "找到样本"],
  ["tier_offer_count", "同层次样本数"],
  ["evaluation_label", "定性标签"],
  ["is_new_quality_productivity_major", "是否新质生产力专业"],
  ["directions", "方向"],
  ["confidence", "置信度"],
  ["score", "规则分"],
  ["rationale", "判定理由"],
  ["policy_source_ids", "政策来源ID"],
  ["policy_evidence_excerpt", "政策证据摘录"],
  ["official_major_source", "专业来源"],
  ["school_sample_source", "院校样本来源"],
  ["estimation_method", "估算方法"],
  ["needs_review", "需复核"],
];

const sourceFields = [
  ["direction", "方向"],
  ["source_id", "来源ID"],
  ["source_title", "来源标题"],
  ["source_url", "URL"],
  ["source_year", "年份"],
  ["issuing_org", "发布机构"],
  ["keyword", "命中词"],
  ["evidence_excerpt", "证据摘录"],
];

buildOverview();
buildTableSheet("专业汇总", payload.summary, summaryFields, "MajorSummaryTable");
buildTableSheet("四层次明细", payload.detail, detailFields, "TierDetailTable");
buildTableSheet("政策来源", payload.sources, sourceFields, "PolicySourcesTable");
buildStatsSheet();

await verifyWorkbook(workbook);
await fs.mkdir(path.dirname(outputPath), { recursive: true });
const xlsx = await SpreadsheetFile.exportXlsx(workbook);
await xlsx.save(outputPath);
console.log(outputPath);

function buildOverview() {
  const sheet = workbook.worksheets.add("说明");
  sheet.showGridLines = false;
  sheet.getRange("A1:H1").merge();
  sheet.getRange("A1").values = [["新质生产力专业定性评价表"]];
  sheet.getRange("A1").format = {
    fill: COLORS.navy,
    font: { bold: true, color: "#FFFFFF", size: 16 },
    horizontalAlignment: "center",
  };

  const stats = payload.stats;
  const rows = [
    ["生成日期", "2026-06-13", "说明", "基于本地 edu_major、edu_school_major、edu_university 和已爬政策证据生成"],
    ["专业数", stats.major_count, "明细行数", stats.detail_row_count],
    ["口径", "是 / 相关 / 弱相关 / 否 / 待复核", "院校层次", "清北、985、211、双非，每个专业各一行"],
    ["核心来源", "gaokao_test_local.edu_major", "政策证据", stats.policy_mentions_csv],
    ["专业候选来源", stats.emerging_unique_csv, "官方目录来源", stats.official_catalog_csv],
  ];
  sheet.getRange("A3:D7").values = rows;
  sheet.getRange("A3:D7").format = {
    fill: COLORS.paleBlue,
    borders: { preset: "all", style: "thin", color: COLORS.border },
    wrapText: true,
  };
  sheet.getRange("A3:A7").format.font = { bold: true };
  sheet.getRange("C3:C7").format.font = { bold: true };

  const labelRows = [["标签", "专业数"], ...Object.entries(stats.label_counts)];
  sheet.getRangeByIndexes(9, 0, labelRows.length, 2).values = labelRows;
  formatHeader(sheet.getRange("A10:B10"));
  sheet.getRangeByIndexes(10, 0, labelRows.length - 1, 2).format.borders = {
    preset: "all",
    style: "thin",
    color: COLORS.border,
  };

  const tierRows = [["院校层次", "找到样本的专业数"], ...Object.entries(stats.tier_found_counts)];
  sheet.getRangeByIndexes(9, 3, tierRows.length, 2).values = tierRows;
  formatHeader(sheet.getRange("D10:E10"));
  sheet.getRangeByIndexes(10, 3, tierRows.length - 1, 2).format.borders = {
    preset: "all",
    style: "thin",
    color: COLORS.border,
  };

  const directionRows = [["方向", "专业数"], ...Object.entries(stats.direction_counts).slice(0, 12)];
  sheet.getRangeByIndexes(17, 0, directionRows.length, 2).values = directionRows;
  formatHeader(sheet.getRange("A18:B18"));
  sheet.getRangeByIndexes(18, 0, directionRows.length - 1, 2).format.borders = {
    preset: "all",
    style: "thin",
    color: COLORS.border,
  };

  const notes = [
    ["方法说明"],
    ["1. “是”表示专业名称或专业类直接命中高精度新质生产力方向词，如人工智能、低空、集成电路、储能、氢能、合成生物、量子、新材料等。"],
    ["2. “相关”表示属于关键支撑专业类或简介/课程/就业方向与政策方向匹配，例如计算机类、电子信息类、材料类、机械类、能源动力类等。"],
    ["3. “弱相关”表示仅有弱关键词或场景关联，建议人工复核后再用于产品展示。"],
    ["4. 院校样本来自本地 edu_school_major 与 edu_university；找不到样本时保留该层次行，并明确标注为估算。"],
  ];
  sheet.getRange("D18:H22").values = notes;
  sheet.getRange("D18:H22").format = {
    fill: COLORS.gray,
    borders: { preset: "all", style: "thin", color: COLORS.border },
    wrapText: true,
  };
  sheet.getRange("D18").format.font = { bold: true };

  sheet.getRange("A:H").format.columnWidthPx = 145;
  sheet.getRange("D:H").format.columnWidthPx = 170;
  sheet.freezePanes.freezeRows(1);
}

function buildStatsSheet() {
  const sheet = workbook.worksheets.add("统计");
  sheet.showGridLines = false;
  sheet.getRange("A1:D1").values = [["维度", "取值", "数量", "备注"]];
  formatHeader(sheet.getRange("A1:D1"));
  const rows = [];
  for (const [label, count] of Object.entries(payload.stats.label_counts)) {
    rows.push(["标签", label, count, "专业汇总口径"]);
  }
  for (const [confidence, count] of Object.entries(payload.stats.confidence_counts)) {
    rows.push(["置信度", confidence, count, "专业汇总口径"]);
  }
  for (const [tier, count] of Object.entries(payload.stats.tier_found_counts)) {
    rows.push(["院校层次样本", tier, count, "找到本地开设样本的专业数"]);
  }
  for (const [direction, count] of Object.entries(payload.stats.direction_counts)) {
    rows.push(["方向", direction, count, "一个专业可命中多个方向"]);
  }
  sheet.getRangeByIndexes(1, 0, rows.length, 4).values = rows;
  sheet.tables.add(`A1:D${rows.length + 1}`, true, "StatsTable").style = "TableStyleMedium2";
  sheet.freezePanes.freezeRows(1);
  setWidths(sheet, [120, 190, 90, 220]);
}

function buildTableSheet(name, rows, fields, tableName) {
  const sheet = workbook.worksheets.add(name);
  sheet.showGridLines = false;
  const values = [fields.map(([, title]) => title)];
  for (const row of rows) {
    values.push(fields.map(([key]) => row[key] ?? ""));
  }
  const colCount = fields.length;
  const rowCount = values.length;
  sheet.getRangeByIndexes(0, 0, rowCount, colCount).values = values;
  const endAddress = `${columnName(colCount)}${rowCount}`;
  sheet.tables.add(`A1:${endAddress}`, true, tableName).style = "TableStyleMedium2";
  sheet.freezePanes.freezeRows(1);
  formatHeader(sheet.getRangeByIndexes(0, 0, 1, colCount));
  sheet.getRangeByIndexes(1, 0, Math.max(rowCount - 1, 1), colCount).format = {
    wrapText: true,
    verticalAlignment: "top",
  };
  applyLabelFormats(sheet, rowCount, fields);
  setSheetWidths(sheet, fields);
}

function applyLabelFormats(sheet, rowCount, fields) {
  const labelIndex = fields.findIndex(([key]) => key === "evaluation_label");
  const reviewIndex = fields.findIndex(([key]) => key === "needs_review");
  if (labelIndex >= 0 && rowCount > 1) {
    const labelCol = columnName(labelIndex + 1);
    const range = sheet.getRange(`${labelCol}2:${labelCol}${rowCount}`);
    range.conditionalFormats.add("containsText", { text: "是", format: { fill: COLORS.yes } });
    range.conditionalFormats.add("containsText", { text: "相关", format: { fill: COLORS.related } });
    range.conditionalFormats.add("containsText", { text: "弱相关", format: { fill: COLORS.weak } });
    range.conditionalFormats.add("containsText", { text: "否", format: { fill: COLORS.no } });
  }
  if (reviewIndex >= 0 && rowCount > 1) {
    const reviewCol = columnName(reviewIndex + 1);
    sheet
      .getRange(`${reviewCol}2:${reviewCol}${rowCount}`)
      .conditionalFormats.add("containsText", { text: "是", format: { fill: COLORS.review } });
  }
}

function formatHeader(range) {
  range.format = {
    fill: COLORS.navy,
    font: { bold: true, color: "#FFFFFF" },
    horizontalAlignment: "center",
    verticalAlignment: "middle",
    wrapText: true,
  };
}

function setSheetWidths(sheet, fields) {
  const widths = fields.map(([key]) => {
    if (["rationale", "policy_evidence_excerpt", "official_major_source", "school_sample_source", "estimation_method"].includes(key)) {
      return 360;
    }
    if (["major_name", "sample_school_name", "directions", "policy_source_ids"].includes(key)) return 180;
    if (["major_code", "score", "confidence", "sample_coverage", "needs_review"].includes(key)) return 90;
    return 130;
  });
  setWidths(sheet, widths);
}

function setWidths(sheet, widths) {
  for (let i = 0; i < widths.length; i += 1) {
    sheet.getRangeByIndexes(0, i, 1, 1).format.columnWidthPx = widths[i];
  }
}

function columnName(index) {
  let name = "";
  let n = index;
  while (n > 0) {
    const rem = (n - 1) % 26;
    name = String.fromCharCode(65 + rem) + name;
    n = Math.floor((n - 1) / 26);
  }
  return name;
}

async function verifyWorkbook(wb) {
  const overview = await wb.inspect({
    kind: "table",
    range: "说明!A1:H22",
    include: "values",
    tableMaxRows: 24,
    tableMaxCols: 8,
    maxChars: 3000,
  });
  console.log(overview.ndjson);
  const errors = await wb.inspect({
    kind: "match",
    searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A",
    options: { useRegex: true, maxResults: 50 },
    summary: "final formula error scan",
  });
  console.log(errors.ndjson);
  await wb.render({ sheetName: "说明", autoCrop: "all", scale: 1, format: "png" });
  await wb.render({ sheetName: "专业汇总", range: "A1:H30", scale: 1, format: "png" });
  await wb.render({ sheetName: "四层次明细", range: "A1:H30", scale: 1, format: "png" });
  await wb.render({ sheetName: "政策来源", range: "A1:H30", scale: 1, format: "png" });
  await wb.render({ sheetName: "统计", range: "A1:D30", scale: 1, format: "png" });
}
