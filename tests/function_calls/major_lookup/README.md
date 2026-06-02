# major_lookup

## 1. 工具原理

`major_lookup` 用来把用户输入的专业名称、简称或专业代码解析为本地标准专业实体。核心数据来自 `edu_major`，确认别名来自 `entity_aliases`。

## 2. 输入与输出

- 主要输入：`major_text`，可选 `limit`。
- 关键输出：`selected_major`、`candidates`、`normalized_slots`。
- 重要字段：专业代码、专业名称、门类、专业类、修业年限、学位、就业描述清洗字段。

## 3. 状态语义

- `ok`：命中标准专业或确认别名。
- `not_found`：本地专业库未命中。
- `needs_clarification`：缺少 `major_text`，或命中多个合理专业候选，不能安全自动选择。
- `partial`：当前工具不使用该状态。

## 4. 测试范围

`major_lookup` 不能只用 mock 单测判断是否完备。它的核心风险在真实 `edu_major` 和 `entity_aliases`
数据排序、候选歧义、同名不同层次专业、非标准招生专业名归一化上。因此测试应分三层：

- Contract 测试：缺少 `major_text`、多余参数、`limit`、统一 envelope、`source_tables` 和 `warnings`。
- Live 检索测试：连接本地 MySQL，直接观察 `selected_major` 和 `candidates` 是否符合真实语义。
- 人工判定测试：对每条 live 结果标注 `correct`、`overconfident`、`should_clarify`、`not_found_ok`、`recall_gap` 等结论，再把确认的问题固化为回归测试。

## 5. 测试结果

- 最近运行日期：2026-06-02。
- 运行环境：本地 MySQL 配置来自 `.env`。当前 `DbConfig.from_env()` 只读进程环境变量，不会自动加载 `.env`，因此手动 CLI 运行前需要先把 `.env` 注入当前进程环境。
- Smoke 命令：

```powershell
Get-Content .env | ForEach-Object {
  if ($_ -match '^\s*([^#][^=]+?)=(.*)$') {
    [Environment]::SetEnvironmentVariable($matches[1].Trim(), $matches[2].Trim(), 'Process')
  }
}
python scripts\run_retrieval_smoke_cases.py --tool major_lookup --strict-targets --report reports\retrieval_smoke_major_lookup_after_fix.json
```

- Smoke 结果：30 条全部通过；`ok` 28 条，预期 `not_found` 2 条，结构层 `failed` 0 条。
- 解释：该 smoke 只能证明主路径和 function-call envelope 稳定，不能证明实体解析语义完备。

## 6. 已知风险与待改善

### 修复后 Live 复测

| 输入 | 当前结果 | 人工判定 |
| --- | --- | --- |
| `计科` | `计算机科学与技术` / `080901` | 正确 |
| `软工` | `软件工程` / `080902` | 正确 |
| `080901` | `计算机科学与技术` / `080901` | 正确 |
| `临床医学`、`临床医学五年制` | `临床医学` / `100201K`，并提示同名多层次默认普通本科 | 已修复：不再误选专科 |
| `口腔医学` | `口腔医学` / `100301K`，并提示同名多层次默认普通本科 | 已修复：不再误选专科 |
| `临床`、`口腔` | 通过确认别名直接命中本科 `100201K` / `100301K` | 已修复 |
| `电信` | `needs_clarification`，候选为 `电子信息工程`、`通信工程` | 已修复：不再过度自信 |
| `电子信息` | `needs_clarification`，候选按别名置信度展示多个本科候选 | 已修复：不再自动选第一个 |
| `网络安全` | `网络空间安全` / `080911TK` | 已修复：通过确认别名避免误召回“网络安全与执法” |
| `大数据` | `数据科学与大数据技术` / `080910T`，候选降为确认别名结果 | 已修复：减少候选噪声 |
| `软件工程专业` | `软件工程` / `080902` | 已修复：剥离口语后缀“专业” |
| `软件工程(中外合作办学)` | `软件工程` / `080902` | 已修复：剥离括号招生项目后缀 |
| `计算机科学与技术（师范）` | `计算机科学与技术` / `080901` | 已修复：剥离括号方向后缀 |
| `AI`、`CS` | `人工智能` / `080717T`，`计算机科学与技术` / `080901` | 已修复：进入确认别名表 |
| `计算机`，`limit=3` | `needs_clarification`，返回 3 个候选 | 已修复：宽泛词不再直接选第一个，并遵守 `limit` |
| `计算机类`、`电子信息类`、`医学`、`工科` | `not_found` | 保守合理，但产品若支持专业类查询，需要另设 category lookup |
| `计算机科学与枝术`、`临床医雪` | `not_found` | 保守合理；若要处理 ASR/OCR，需要单独模糊纠错层 |
| 空输入 | `needs_clarification` | 正确 |
| 多余参数，如 `province` | registry 返回 `error` | 正确 |
| 注入式输入 | `not_found` | 安全边界正常 |

### 本轮已修复

- 同名不同层次专业排序：精确同名时默认优先普通本科代码，仍把其他层次放入候选并给 warning。
- 多候选别名保护：确认别名命中多个标准专业时返回 `needs_clarification`。
- 宽泛 fuzzy 保护：fallback 命中多个非精确候选时返回 `needs_clarification`，不再自动选第一条。
- 招生后缀归一：剥离尾部 `专业`、括号方向/项目、`四年制`/`五年制` 等学制后缀。
- 别名 seed 补强：新增 `AI`、`CS`、`网络安全`、`网安`，并让 `电子信息` 保持多候选。
- CLI 对齐：`major_lookup` CLI 已支持 `--limit`。

### 剩余边界

- `护理` 是专科标准专业名；若用户本科语境下想查 `护理学`，仍需要上游语义层或别名策略进一步判断。
- `数据科学` 是真实本科专业，同时用户也可能口语化指 `数据科学与大数据技术`；当前保留精确专业优先。
- 专业类/门类词如 `计算机类`、`医学`、`工科` 仍保守 `not_found`，应由 category/discipline resolver 处理。
- OCR/ASR 错别字仍不在 `major_lookup` 内做纠错，避免把错字强行猜成具体专业。

### 下一步测试方法

后续仍应按 live adjudication 方式维护，而不是只新增 `_test.py`：

1. 建一份 `major_lookup` 专属 case 表，覆盖精确名、代码、确认别名、歧义别名、同名不同层次、专业类、口语后缀、括号方向、英文缩写、错别字和不存在专业。
2. 每条 case 保存真实 `selected_major`、前 N 个 `candidates`、`status`、`warnings`。
3. 人工给每条标注期望行为：应命中哪个 code、是否必须澄清、是否允许 `not_found`、是否需要保留原始招生专业名。
4. 将确认的问题拆成两类：数据/别名 seed 问题和解析规则问题。
5. 修复前先把高风险失败点写成回归测试，修复后重新跑 live adjudication 和现有 smoke。

## 7. 关联文件

- 实现：[scripts/retrieval_tools.py](../../../scripts/retrieval_tools.py)
- SQL 构造：[scripts/local_retrieval_mvp.py](../../../scripts/local_retrieval_mvp.py)
- 别名 seed：[scripts/setup_entity_aliases.py](../../../scripts/setup_entity_aliases.py)
- Live 判定 case 表：[live_adjudication_cases.md](live_adjudication_cases.md)
