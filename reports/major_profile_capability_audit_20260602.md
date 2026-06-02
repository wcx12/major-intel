# major_profile 能力边界审计

日期：2026-06-02

## 审计目标

本次审计不是验证 `major_profile` 是否能跑通，而是判断它返回的真实检索内容是否足以支撑上层 agent 安全回答“专业概况”问题。

审计对象：`scripts/retrieval_tools.py::RetrievalTools.major_profile`

审计口径：

- 专业实体必须解析正确；不能把宽泛词、错别字、整句意图或歧义简称包装成确定画像。
- `major_profile` 只允许表达专业通用事实，不能替代某校某专业就业、录取、培养质量或可报结论。
- 上游 `major_lookup` 的候选、warning、来源表不能在画像层被丢失。
- 专业画像字段缺失时应显式进入 `data_gaps` 或 `warnings`，不能用空数组伪装成完整画像。
- 返回的就业方向文本应是可用的结构化方向，而不是过长、混杂的介绍段落。

本轮命令从本地 `.env` 加载 `GAOKAO_DB_*` 环境变量运行；未输出数据库密码。

## 样本矩阵

真实库样本均通过：

```powershell
python scripts/retrieval_tools.py major_profile --major "<专业输入>"
```

| 编号 | 输入 | 状态 | 选中专业 | 画像字段摘要 | 人工判定 |
|---|---|---|---|---|---|
| MP001 | 计算机科学与技术 | `ok` | 计算机科学与技术 `080901` | 薪资空，就业方向 0，`data_gaps` 空 | `gap`：实体正确，但画像不完整且未标缺口 |
| MP002 | 软件工程 | `ok` | 软件工程 `080902` | 薪资有值，就业方向 1 条长段落 | `risk`：可用但文本结构差 |
| MP003 | 人工智能 | `ok` | 人工智能 `080717T` | 薪资有值，就业方向 1 条应用列表段落 | `risk`：可用但不是清晰就业方向 |
| MP004 | 数据科学与大数据技术 | `ok` | 数据科学与大数据技术 `080910T` | 薪资有值，就业方向 6 条 | `pass`：专业通用画像基本可用 |
| MP005 | 网络空间安全 | `ok` | 网络空间安全 `080911TK` | 薪资有值，就业方向 11 条 | `pass`：专业通用画像基本可用 |
| MP006 | 电子信息工程 | `ok` | 电子信息工程 `080701` | 薪资空，就业方向 0，`data_gaps` 空 | `gap`：实体正确，但画像不完整且未标缺口 |
| MP007 | 通信工程 | `ok` | 通信工程 `080703` | 薪资有值，就业方向 5 条 | `pass/risk`：内容可用，部分文本仍偏长 |
| MP008 | 自动化 | `ok` | 自动化 `080801` | 薪资空，就业方向 0，`data_gaps` 空 | `gap`：实体正确，但画像不完整且未标缺口 |
| MP009 | 电气工程及其自动化 | `ok` | 电气工程及其自动化 `080601` | 薪资空，就业方向 0，`data_gaps` 空 | `gap`：实体正确，但画像不完整且未标缺口 |
| MP010 | 法学 | `ok` | 法学 `030101K` | 薪资有值，就业方向 11 条 | `risk`：方向文本混入大量叙述和薪资泛化 |
| MP011 | 会计学 | `ok` | 会计学 `120203K` | 薪资有值，就业方向 6 条 | `risk`：方向文本过长，需摘要化 |
| MP012 | 临床医学 | `ok` | 临床医学 `100201K` | 薪资有值，就业方向 4 条，profile warning 空 | `risk`：实体已优先本科，但吞掉同名层次 warning |
| MP013 | 口腔医学 | `ok` | 口腔医学 `100301K` | 薪资有值，就业方向 17 条 | `pass/risk`：实体正确，文本需压缩 |
| MP014 | 护理 | `ok` | 护理 `320201` | 薪资 `0`，就业方向 1 条“暂无数据”，profile warning 空 | `risk`：口语输入与护理学/专科护理存在层次语义风险 |
| MP015 | 080901 | `ok` | 计算机科学与技术 `080901` | 薪资空，就业方向 0 | `gap`：代码解析正确，画像缺口未标 |
| MP016 | 080910T | `ok` | 数据科学与大数据技术 `080910T` | 薪资有值，就业方向 6 条 | `pass` |
| MP017 | 100201K | `ok` | 临床医学 `100201K` | 薪资有值，就业方向 4 条 | `pass`：代码足以消除层次歧义 |
| MP018 | 计科 | `ok` | 计算机科学与技术 `080901` | 别名解析成功，画像空缺未标 | `gap`：别名可用，画像缺口未标 |
| MP019 | 软工 | `ok` | 软件工程 `080902` | 别名解析成功 | `pass/risk`：文本结构仍差 |
| MP020 | 电气 | `ok` | 电气工程及其自动化 `080601` | 别名解析成功，画像空缺未标 | `gap`：别名可用，画像缺口未标 |
| MP021 | 电信 | `needs_clarification` | 无 | profile 只返回 1 个候选 | `fail/risk`：状态保守，但候选被 `limit=1` 压窄 |
| MP022 | 电子信息 | `needs_clarification` | 无 | profile 只返回 1 个候选；raw lookup 有 3 个候选 | `fail/risk`：状态保守，但候选不足以澄清 |
| MP023 | 计算机类 | `not_found` | 无 | 不猜测具体专业 | `pass`：专业类不应被当成具体专业 |
| MP024 | 工科 | `not_found` | 无 | 不猜测具体专业 | `pass`：宽泛门类不应被当成具体专业 |
| MP025 | 软件工程专业 | `ok` | 软件工程 `080902` | 后缀归一成功 | `pass/risk`：实体正确，文本结构仍差 |
| MP026 | 软件工程(中外合作办学) | `ok` | 软件工程 `080902` | 招生项目后缀归一成功 | `pass/risk`：实体正确，但需避免丢失“中外合作”上下文 |
| MP027 | 计算机科学与技术（师范） | `ok` | 计算机科学与技术 `080901` | 括号方向归一成功，画像空缺未标 | `gap/risk`：基础专业正确，但师范方向上下文未保留 |
| MP028 | 临床医学五年制 | `ok` | 临床医学 `100201K` | 学制后缀归一成功 | `pass` |
| MP029 | 计算机科学与枝术 | `not_found` | 无 | 不做错字猜测 | `pass`：保持保守 |
| MP030 | 想学计算机 | `not_found` | 无 | 不从整句抽槽 | `pass`：应由自然语言入口先抽槽 |
| MP031 | 星际航道规划与管理 | `not_found` | 无 | 不猜测不存在专业 | `pass` |
| MP032 | SQL 注入式输入 | `not_found` | 无 | 未扩大查询 | `pass`：安全边界可接受 |

## 关键发现

### 1. `major_profile` 会吞掉 `major_lookup` 的 warning

`major_lookup("临床医学", limit=5)` 返回 `ok`，选中本科 `100201K`，同时在候选里保留专科/相近专业，并给出 warning：

> 同名专业存在多个层次，当前默认优先普通本科专业代码；如需专科或职业本科，请提供专业代码。

但 `major_profile("临床医学")` 重新包装结果后 `warnings: []`。

同类问题也出现在 `护理`：`major_lookup("护理")` 知道候选含 `320201` 和 `520201` 并提示层次风险，但 `major_profile("护理")` 返回画像时 warning 丢失。

正确边界：画像层不能丢失实体解析层的风险提示。

### 2. 歧义输入的候选被 `limit=1` 压窄

`major_profile` 当前内部调用：

```python
major_result = self.major_lookup(major_text, limit=1)
```

这避免了错选画像，但会让澄清候选不足。

实测：

- `major_profile("电信")` 返回 `needs_clarification`，但候选只有 `电子信息工程`。
- `major_lookup("电信", limit=5)` 返回 `电子信息工程`、`通信工程` 两个候选。
- `major_profile("电子信息")` 返回 `needs_clarification`，候选只有 1 个。
- `major_lookup("电子信息", limit=10)` 返回 `电子信息工程`、`电子信息科学与技术`、`电子信息材料` 三个候选。

正确边界：高阶工具继承 lookup 的澄清行为时，应保留足够候选，不应因画像查询把候选压成 1 条。

### 3. 画像字段缺失没有进入 `data_gaps`

多条常见专业解析正确，但专业画像核心字段为空：

- `计算机科学与技术`：薪资空，就业方向 0。
- `电子信息工程`：薪资空，就业方向 0。
- `自动化`：薪资空，就业方向 0。
- `电气工程及其自动化`：薪资空，就业方向 0。

这些结果仍返回 `ok` 且 `data_gaps: []`。

正确边界：实体解析 `ok` 不等于画像完整。至少应标注 `专业通用薪资参考`、`专业通用就业方向` 这类缺口。

### 4. 就业方向文本质量不稳定

部分专业的 `job_directions` 是可用枚举，例如 `数据科学与大数据技术`、`网络空间安全`。

但部分专业返回的是长篇段落或混杂口径：

- `软件工程`：1 条长段落，主要是行业前景。
- `法学`：混入律师收入、就业热门方向、叙述性材料。
- `会计学`：混入内资企业、外企、事务所长段落。
- `护理`：`job_clean` 为“暂无数据”，但仍作为 1 条就业方向返回。

正确边界：`job_directions` 应过滤“暂无数据”、压缩长段落，必要时将不可结构化文本放入 `warnings`。

### 5. Function-call 合约边界可用

直接调 dispatcher 验证：

- `call_retrieval_function("major_profile", {})` 返回 `needs_clarification`，缺 `major_text`。
- `call_retrieval_function("major_profile", {"major_text": "080901", "school_text": "10336"})` 返回 `error`，拒绝未声明的 `school_text`。

这说明 registry schema 层能守住“major_profile 不是某校某专业画像”的参数边界。

## 当前结论

`major_profile` 审计时可以作为“专业实体 + 部分通用画像”的工具使用，但还不能判定为完备。

已守住的边界：

- 标准专业名、代码、确认别名整体解析可用。
- 宽泛专业类、门类、错字、整句意图、不存在专业和注入式输入不会被猜成具体专业。
- Registry 合约拒绝缺槽和额外学校参数。
- scope notes 明确“专业通用级数据，不代表某学校某专业毕业生真实结果”。

未守住或未充分守住的边界：

- 画像层丢失 `major_lookup` 的层次/歧义 warning。
- 画像层用 `limit=1` 压窄澄清候选。
- 画像核心字段为空时不标 `data_gaps`。
- 就业方向文本结构化质量不稳定，且“暂无数据”没有过滤。
- 后缀归一会丢失 `师范`、`中外合作办学` 这类上下文，回答时容易越界。

## 建议修正顺序

1. `major_profile` 调用 `major_lookup` 时不要传 `limit=1`，或至少在非 `ok` 时用默认候选宽度重新解析。
2. `major_profile` 合并 `major_result["warnings"]`、`data_gaps`、`needs_clarification` 和 `source_tables`。
3. 对 `salary_reference`、`job_directions` 增加有效性判断：全空、`0`、`暂无数据`、空字符串应标缺口或 warning。
4. 将后缀归一上下文放入 `normalized_slots` 或 `warnings`，例如“已按基础专业查询，原输入包含师范/中外合作办学方向”。
5. 为本报告里的失败/风险样本补回归测试，但测试只用于防退化；完备性仍要继续做 live 人工判定。

## 修复后复验

本轮已完成上述 5 项中的工具层可执行部分，并固化回归测试：

- `major_profile` 改为使用 `major_lookup` 默认候选宽度，避免澄清候选被压成 1 条。
- `major_profile` 会保留 `major_lookup` 的 warnings。
- 空薪资、`0` 薪资、空就业方向、`暂无数据` 就业方向会进入 `data_gaps` 和 `warnings`。
- 后缀归一上下文会进入 `normalized_slots.major_text_context`，并给出“已按基础专业查询”的 warning。
- 单条就业方向文本超过 120 字时会截断为摘要片段，并给出 warning。
- 新增 6 条回归测试覆盖 warning 保留、候选宽度、空画像缺口、占位就业方向过滤、后缀上下文保留和长文本截断。

验证命令：

```powershell
python -m unittest tests.test_retrieval_tools.RetrievalToolsTests.test_major_profile_preserves_lookup_cross_level_warning tests.test_retrieval_tools.RetrievalToolsTests.test_major_profile_keeps_clarification_candidates_wide tests.test_retrieval_tools.RetrievalToolsTests.test_major_profile_marks_missing_salary_and_job_direction_gaps tests.test_retrieval_tools.RetrievalToolsTests.test_major_profile_filters_placeholder_job_direction_as_gap
python -m unittest tests.test_retrieval_tools
python -m unittest discover -s tests
```

验证结果：

- 6 条新增回归测试通过。
- `tests.test_retrieval_tools` 共 58 条通过。
- 全量 unittest discover 共 545 条通过；输出中有既有 `ResourceWarning`，无测试失败。

真实库关键样本复验摘要：

| 输入 | 修复后结果 |
|---|---|
| 临床医学 | `ok`，选中本科 `100201K`，保留同名层次 warning |
| 护理 | `ok`，保留同名层次 warning，并标出薪资/就业方向缺口 |
| 电信 | `needs_clarification`，候选数 2 |
| 电子信息 | `needs_clarification`，候选数 3 |
| 计算机科学与技术 | `ok`，标出薪资/就业方向缺口 |
| 计算机科学与技术（师范） | `ok`，按基础专业 `080901` 查询，`major_text_context` 保留 `（师范）` |
| 软件工程 | `ok`，长就业方向截断到 123 字以内，并标 warning |

后续仍可优化：

- 当前长文本处理是截断摘要片段，不是语义级总结；如需更漂亮的自然语言摘要，应放到上层 agent 或专门清洗流程。
