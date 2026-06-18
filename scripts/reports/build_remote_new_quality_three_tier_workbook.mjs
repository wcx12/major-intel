import fs from "node:fs/promises";
import path from "node:path";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const inputPath = process.argv[2] ?? "reports/new_quality_major_three_tier_20260614/remote_major_new_quality_three_tier_workbook_data_20260614.json";
const outputPath = process.argv[3] ?? "reports/new_quality_major_three_tier_20260614/remote_major_new_quality_three_tier_evaluation_20260614.xlsx";

const payload = JSON.parse(await fs.readFile(inputPath, "utf8"));
const workbook = Workbook.create();

const COLORS = {
  navy: "#1F4E78",
  paleBlue: "#EAF4FB",
  gray: "#F3F4F6",
  border: "#D7DEE8",
  yes: "#C6EFCE",
  related: "#DDEBF7",
  weak: "#FFF2CC",
  no: "#E7E6E6",
  review: "#FCE4D6",
};

const evalFields = [
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
  ["tier1_examples", "第1层样例"],
  ["tier1_offer_count", "第1层样本数"],
  ["tier1_interpretation", "第1层解读"],
  ["tier2_examples", "第2层样例"],
  ["tier2_offer_count", "第2层样本数"],
  ["tier2_interpretation", "第2层解读"],
  ["tier3_examples", "第3层样例"],
  ["tier3_offer_count", "第3层样本数"],
  ["tier3_interpretation", "第3层解读"],
  ["policy_source_ids", "政策来源ID"],
  ["policy_evidence_excerpt", "政策证据摘录"],
  ["official_major_source", "专业来源"],
  ["sample_basis", "样本/估算依据"],
  ["estimation_note", "估算说明"],
  ["needs_review", "需复核"],
];

const detailFields = [
  ["major_special_id", "专业ID"],
  ["major_code", "专业代码"],
  ["major_name", "专业名称"],
  ["school_tier", "院校层级"],
  ["school_tier_name", "院校层级名称"],
  ["sample_school_id", "样本院校ID"],
  ["sample_school_name", "样本院校"],
  ["sample_school_rank", "排名"],
  ["sample_school_province", "省份"],
  ["offer_count_in_tier", "同层级样本数"],
  ["evaluation_label", "定性标签"],
  ["directions", "方向"],
  ["confidence", "置信度"],
  ["tier_interpretation", "层级解读"],
  ["sample_basis", "样本依据"],
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
buildTableSheet("专业判断", payload.rows, evalFields, "MajorEvalTable");
buildTableSheet("层级样例明细", payload.details, detailFields, "TierExamplesTable");
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
  sheet.getRange("A1").values = [["远程专业新质生产力三层院校口径评价"]];
  sheet.getRange("A1").format = {
    fill: COLORS.navy,
    font: { bold: true, color: "#FFFFFF", size: 16 },
    horizontalAlignment: "center",
  };
  const stats = payload.stats;
  const rows = [
    ["生成日期", "2026-06-14", "专业数", stats.major_count],
    ["院校层级来源", stats.remote_tier_csv, "政策证据来源", stats.policy_mentions_csv],
    ["专业来源", stats.remote_major_csv, "开设样本", "远程 edu_school_major 只读查询"],
    ["标签口径", "是 / 相关 / 弱相关 / 否", "说明", "专业定性是专业属性；三层院校列用于展示样本和层级解读"],
  ];
  sheet.getRange("A3:D6").values = rows;
  sheet.getRange("A3:D6").format = { fill: COLORS.paleBlue, wrapText: true, borders: { preset: "all", style: "thin", color: COLORS.border } };
  sheet.getRange("A3:A6").format.font = { bold: true };
  sheet.getRange("C3:C6").format.font = { bold: true };

  writeKeyValues(sheet, "A9", "标签分布", stats.label_counts);
  writeKeyValues(sheet, "D9", "三层样本覆盖", stats.major_with_tier_sample_counts);
  writeKeyValues(sheet, "A18", "方向分布", stats.direction_counts, 12);

  const notes = [
    ["层级解读"],
    ["第1层：头部/强研究型高校，重点看前沿科研、交叉学科和原创技术供给。"],
    ["第2层：区域重点/特色优势高校，重点看工程转化、区域产业链和特色学科建设。"],
    ["第3层：普通应用/职业供给高校，重点看应用技能、岗位供给和场景落地。"],
    ["样本缺失时仍保留评价，依据专业属性、政策证据和官方专业来源估算。"],
  ];
  sheet.getRange("D18:H22").values = notes;
  sheet.getRange("D18:H22").format = { fill: COLORS.gray, wrapText: true, borders: { preset: "all", style: "thin", color: COLORS.border } };
  sheet.getRange("D18").format.font = { bold: true };
  setWidths(sheet, [130, 190, 130, 210, 160, 160, 160, 160]);
}

function writeKeyValues(sheet, anchor, title, object, limit = 20) {
  const entries = Object.entries(object).slice(0, limit);
  const values = [[title, "数量"], ...entries];
  const cell = parseCell(anchor);
  sheet.getRangeByIndexes(cell.row, cell.col, values.length, 2).values = values;
  formatHeader(sheet.getRangeByIndexes(cell.row, cell.col, 1, 2));
  sheet.getRangeByIndexes(cell.row + 1, cell.col, Math.max(values.length - 1, 1), 2).format.borders = { preset: "all", style: "thin", color: COLORS.border };
}

function buildStatsSheet() {
  const sheet = workbook.worksheets.add("统计");
  sheet.showGridLines = false;
  const rows = [["维度", "取值", "数量"]];
  for (const [k, v] of Object.entries(payload.stats.label_counts)) rows.push(["标签", k, v]);
  for (const [k, v] of Object.entries(payload.stats.confidence_counts)) rows.push(["置信度", k, v]);
  for (const [k, v] of Object.entries(payload.stats.major_with_tier_sample_counts)) rows.push(["有样本专业数-层级", k, v]);
  for (const [k, v] of Object.entries(payload.stats.direction_counts)) rows.push(["方向", k, v]);
  sheet.getRangeByIndexes(0, 0, rows.length, 3).values = rows;
  sheet.tables.add(`A1:C${rows.length}`, true, "StatsTable").style = "TableStyleMedium2";
  sheet.freezePanes.freezeRows(1);
  setWidths(sheet, [160, 220, 90]);
}

function buildTableSheet(name, rows, fields, tableName) {
  const sheet = workbook.worksheets.add(name);
  sheet.showGridLines = false;
  const values = [fields.map(([, title]) => title)];
  for (const row of rows) values.push(fields.map(([key]) => row[key] ?? ""));
  const colCount = fields.length;
  const rowCount = values.length;
  sheet.getRangeByIndexes(0, 0, rowCount, colCount).values = values;
  const end = `${columnName(colCount)}${rowCount}`;
  sheet.tables.add(`A1:${end}`, true, tableName).style = "TableStyleMedium2";
  sheet.freezePanes.freezeRows(1);
  formatHeader(sheet.getRangeByIndexes(0, 0, 1, colCount));
  sheet.getRangeByIndexes(1, 0, Math.max(rowCount - 1, 1), colCount).format = { wrapText: true, verticalAlignment: "top" };
  applyConditionalFormats(sheet, rowCount, fields);
  setSheetWidths(sheet, fields);
}

function applyConditionalFormats(sheet, rowCount, fields) {
  const labelIndex = fields.findIndex(([key]) => key === "evaluation_label");
  const reviewIndex = fields.findIndex(([key]) => key === "needs_review");
  if (labelIndex >= 0 && rowCount > 1) {
    const col = columnName(labelIndex + 1);
    const range = sheet.getRange(`${col}2:${col}${rowCount}`);
    range.conditionalFormats.add("containsText", { text: "是", format: { fill: COLORS.yes } });
    range.conditionalFormats.add("containsText", { text: "相关", format: { fill: COLORS.related } });
    range.conditionalFormats.add("containsText", { text: "弱相关", format: { fill: COLORS.weak } });
    range.conditionalFormats.add("containsText", { text: "否", format: { fill: COLORS.no } });
  }
  if (reviewIndex >= 0 && rowCount > 1) {
    const col = columnName(reviewIndex + 1);
    sheet.getRange(`${col}2:${col}${rowCount}`).conditionalFormats.add("containsText", { text: "是", format: { fill: COLORS.review } });
  }
}

function setSheetWidths(sheet, fields) {
  const widths = fields.map(([key]) => {
    if (key.includes("interpretation") || key.includes("evidence") || key.includes("rationale") || key.includes("basis") || key.includes("source")) return 340;
    if (key.includes("examples") || key.includes("official")) return 300;
    if (key.includes("name") || key === "directions") return 180;
    return 110;
  });
  setWidths(sheet, widths);
}

function setWidths(sheet, widths) {
  for (let i = 0; i < widths.length; i += 1) sheet.getRangeByIndexes(0, i, 1, 1).format.columnWidthPx = widths[i];
}

function formatHeader(range) {
  range.format = { fill: COLORS.navy, font: { bold: true, color: "#FFFFFF" }, horizontalAlignment: "center", verticalAlignment: "middle", wrapText: true };
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

function parseCell(address) {
  const match = /^([A-Z]+)(\d+)$/.exec(address);
  let col = 0;
  for (const ch of match[1]) col = col * 26 + ch.charCodeAt(0) - 64;
  return { row: Number(match[2]) - 1, col: col - 1 };
}

async function verifyWorkbook(wb) {
  const overview = await wb.inspect({ kind: "table", range: "说明!A1:H24", include: "values", tableMaxRows: 24, tableMaxCols: 8, maxChars: 3000 });
  console.log(overview.ndjson);
  const errors = await wb.inspect({ kind: "match", searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A", options: { useRegex: true, maxResults: 50 } });
  console.log(errors.ndjson);
  await wb.render({ sheetName: "说明", autoCrop: "all", scale: 1, format: "png" });
  await wb.render({ sheetName: "专业判断", range: "A1:H30", scale: 1, format: "png" });
  await wb.render({ sheetName: "层级样例明细", range: "A1:H30", scale: 1, format: "png" });
  await wb.render({ sheetName: "政策来源", range: "A1:H30", scale: 1, format: "png" });
  await wb.render({ sheetName: "统计", range: "A1:C30", scale: 1, format: "png" });
}
