# 检索工具人工测试命令手册

更新时间：2026-05-21

这份文档用于手动逐个测试 `scripts/retrieval_tools.py` 里的 27 个底层检索工具。所有命令都走本地 MySQL，不调用联网搜索，也不依赖 DeepSeek。

## 运行前准备

PowerShell 中先设置数据库环境变量：

```powershell
$env:GAOKAO_DB_HOST = "127.0.0.1"
$env:GAOKAO_DB_PORT = "3306"
$env:GAOKAO_DB_USER = "root"
$env:GAOKAO_DB_NAME = "gaokao_test_local"
$env:GAOKAO_DB_PASSWORD = "<你的本地密码>"
```

通用检查命令：

```powershell
python scripts/retrieval_tools.py <工具名> --help
python scripts/retrieval_function_registry.py list-names
python scripts/run_retrieval_smoke_cases.py --sample-per-tool 1 --report reports/retrieval_smoke_sample_27_tools.json
```

看结果时重点检查这些字段：

- `status`：`ok`、`partial`、`not_found`、`needs_clarification` 都可能是合理结果；是否合理要结合问题口径看。
- `normalized_slots`：学校、专业、省份、科类、年份等是否被正确归一。
- `data`：是否返回了可用结构化数据。
- `scope_notes` / `warnings`：是否说明了学校级、专业通用级、校专业级、专业组级等口径。
- `data_gaps`：缺口是否说清楚，不能因为缺数据而编结论。
- `source_tables`：是否能看出本地 SQL 来源。

## 1. `school_lookup`

用途：解析学校名称、简称或代码。

推荐命令：

```powershell
python scripts/retrieval_tools.py school_lookup --school "杭电"
```

可换参数：

```powershell
python scripts/retrieval_tools.py school_lookup --school "杭州电子科技大学"
python scripts/retrieval_tools.py school_lookup --school "10336"
```

重点看：`normalized_slots.school_name` 是否为目标学校；简称命中时 `source_tables` 应包含 `entity_aliases`。

## 2. `major_lookup`

用途：解析专业名称、简称或代码。

推荐命令：

```powershell
python scripts/retrieval_tools.py major_lookup --major "计科"
```

可换参数：

```powershell
python scripts/retrieval_tools.py major_lookup --major "计算机科学与技术"
python scripts/retrieval_tools.py major_lookup --major "080901"
```

重点看：短简称是否通过 `entity_aliases` 命中正确专业，避免误命中包含短词的其他专业。

## 3. `school_profile`

用途：查询学校级画像。

推荐命令：

```powershell
python scripts/retrieval_tools.py school_profile --school "杭州电子科技大学"
```

可换参数：

```powershell
python scripts/retrieval_tools.py school_profile --school "浙大"
```

重点看：学校基础、双一流、学科评估、学校级就业/升学摘要是否出现；学校级就业不能当成某专业就业。

## 4. `major_profile`

用途：查询专业通用画像。

推荐命令：

```powershell
python scripts/retrieval_tools.py major_profile --major "软件工程"
```

可换参数：

```powershell
python scripts/retrieval_tools.py major_profile --major "软工"
python scripts/retrieval_tools.py major_profile --major "电信"
python scripts/retrieval_tools.py major_profile --major "计算机科学与技术（师范）"
python scripts/retrieval_tools.py major_profile --major "计算机科学与技术"
```

重点看：

- 标准名、代码、确认别名是否解析到正确 `major_code`。
- 歧义输入是否返回 `needs_clarification` 并保留多个候选。
- 同名本科/专科专业是否保留层次 warning。
- 薪资或就业方向缺失时是否进入 `data_gaps`。
- `师范`、`中外合作办学` 等后缀是否保留在 `normalized_slots.major_text_context` 或 warning。
- 这只是专业通用画像，不是某学校该专业的就业、培养质量或录取结论。

## 5. `school_major_list`

用途：查询某学校本地库记录的开设专业列表。

推荐命令：

```powershell
python scripts/retrieval_tools.py school_major_list --school "杭州电子科技大学" --major-category "计算机类" --limit 20
```

可选参数：

- `--major-category`：专业门类或专业类筛选词，例如 `工学`、`计算机类`。
- `--limit`：返回数量，默认 100。

重点看：返回的是学校开设专业，不等于某省某年招生计划。

## 6. `major_school_list`

用途：查询开设某专业的学校列表。

推荐命令：

```powershell
python scripts/retrieval_tools.py major_school_list --major "计算机科学与技术" --province-filter "浙江" --school-level-filter "本科" --limit 20
```

可选参数：

- `--province-filter`：学校所在省份。
- `--school-level-filter`：学校层次粗筛，例如 `本科`。
- `--limit`：返回数量，默认 50。

重点看：这是开设学校列表，不代表当年在考生省份招生。

## 7. `school_major_profile`

用途：查询某校某专业综合画像。

推荐命令：

```powershell
python scripts/retrieval_tools.py school_major_profile --school "杭州电子科技大学" --major "计算机科学与技术" --province "浙江" --subject-type "物理" --year 2025
```

可选参数：

- `--province`：考生或招生省份。
- `--subject-type`：`物理`、`历史`、`综合` 等。
- `--year`：招生或录取年份。

重点看：如果缺少校专业级就业、薪资、官网介绍等，返回 `partial` 和 `data_gaps` 是合理的。

## 8. `score_to_rank`

用途：同省、同科类、同年份分数转位次。

推荐命令：

```powershell
python scripts/retrieval_tools.py score_to_rank --province "浙江" --subject-type "综合" --score 620 --year 2025
```

可换参数：

```powershell
python scripts/retrieval_tools.py score_to_rank --province "广东" --subject-type "物理" --score 580 --year 2025
```

重点看：`data` 中是否有位次区间；跨省、跨科类不能比较分数。

## 9. `rank_to_school_match`

用途：按分数或位次返回学校层面的冲/稳/保参考。

推荐命令：

```powershell
python scripts/retrieval_tools.py rank_to_school_match --province "浙江" --subject-type "综合" --score 620 --year 2025 --preferred-regions 浙江 江苏 上海 --limit 20
```

可选参数：

- `--score`：分数；使用分数时通常要给 `--subject-type`。
- `--rank`：位次；给了位次可不依赖分数换算。
- `--reference-years 2024 2023`：限定历史参考年份。
- `--preferred-regions 浙江 江苏 上海`：限定学校所在地。
- `--school-level-filter`：学校层次或类型粗筛。
- `--limit`：返回数量，默认 30。

重点看：结果是历史位次参考，不是录取保证。

## 10. `rank_to_major_match`

用途：按分数或位次 + 专业偏好返回学校-专业行的冲/稳/保参考。

推荐命令：

```powershell
python scripts/retrieval_tools.py rank_to_major_match --province "浙江" --major "计算机" --subject-type "综合" --score 620 --year 2025 --preferred-regions 浙江 江苏 上海 --limit 20
```

可选参数：

- `--score` 或 `--rank`：二选一即可。
- `--reference-years 2024 2023`：限定历史参考年份。
- `--preferred-regions`：限定学校所在地。
- `--school-level-filter`：学校层次或类型粗筛。
- `--limit`：返回数量，默认 30。

重点看：是否返回学校-专业行；专业大类、试验班、方向名要结合 `warnings` 理解。

## 11. `specialty_group_lookup`

用途：查询专业组和组内专业。

推荐命令：

```powershell
python scripts/retrieval_tools.py specialty_group_lookup --school "杭州电子科技大学" --major "计算机" --province "浙江" --subject-type "综合" --year 2025 --limit 10
```

可选参数：

- `--major`：只找包含该专业的专业组。
- `--province`、`--subject-type`、`--year`：过滤招生口径。
- `--group-code`：指定专业组代码。
- `--limit`：返回组数量，默认 20。

重点看：专业组构成不等于入学后真实分流比例。

## 12. `subject_requirement_lookup`

用途：查询专业在专业组样本中的选科要求。

推荐命令：

```powershell
python scripts/retrieval_tools.py subject_requirement_lookup --major "计算机科学与技术" --school "杭州电子科技大学" --province "浙江" --subject-type "综合" --year 2025 --limit 20
```

可选参数：

- `--school`：限定学校。
- `--province`、`--subject-type`、`--year`：限定招生上下文。
- `--limit`：返回数量，默认 50。

重点看：选科要求必须按省份和年份理解。

## 13. `school_department_major_list`

用途：查询学校院系与院系下专业。

推荐命令：

```powershell
python scripts/retrieval_tools.py school_department_major_list --school "杭州电子科技大学" --department "计算机" --limit 50
```

可选参数：

- `--department`：院系名称筛选。
- `--major`：专业名称筛选。
- `--limit`：返回数量，默认 100。

重点看：院系专业关系不等于某省招生计划。

## 14. `plan_history`

用途：查询学校/专业招生计划历史。

推荐命令：

```powershell
python scripts/retrieval_tools.py plan_history --school "杭州电子科技大学" --major "计算机科学与技术" --province "浙江" --years 2025 2024 --limit 50
```

可选参数：

- `--major`：限定专业。
- `--province`：限定招生省份。
- `--years 2025 2024`：限定年份列表。
- `--limit`：返回数量，默认 100。

重点看：计划数不等于实际录取人数。

## 15. `employment_summary`

用途：查询学校级就业/升学摘要。

推荐命令：

```powershell
python scripts/retrieval_tools.py employment_summary --school "杭州电子科技大学" --limit 5
```

可选参数：

- `--limit`：返回年份或记录数量，默认 5。

重点看：学校级就业/升学不能当成某专业真实就业。

## 16. `source_trace_lookup`

用途：查看某个工具的数据来源、口径和可信度说明。

推荐命令：

```powershell
python scripts/retrieval_tools.py source_trace_lookup --tool-name school_major_profile
```

可选参数：

```powershell
python scripts/retrieval_tools.py source_trace_lookup
python scripts/retrieval_tools.py source_trace_lookup --tool-name civil_service_mapping
```

重点看：`source_tables`、`scope_notes`、`reliability`。

## 17. `transfer_policy_lookup`

用途：查询转专业政策线索。

推荐命令：

```powershell
python scripts/retrieval_tools.py transfer_policy_lookup --school "杭州电子科技大学"
```

重点看：当前多为第三方线索，必须官方复核后才能给高风险结论。

## 18. `fee_and_campus_lookup`

用途：查询学费、校区、住宿等线索。

推荐命令：

```powershell
python scripts/retrieval_tools.py fee_and_campus_lookup --school "杭州电子科技大学" --major "计算机科学与技术" --province "浙江" --year 2025 --limit 20
```

可选参数：

- `--major`：限定专业。
- `--province`：限定招生省份。
- `--year`：限定年份。
- `--limit`：返回数量，默认 50。

重点看：校区字段不稳定时，工具应该返回缺口而不是猜测。

## 19. `specialty_group_risk`

用途：基于专业组构成做调剂风险初筛。

推荐命令：

```powershell
python scripts/retrieval_tools.py specialty_group_risk --school "杭州电子科技大学" --province "浙江" --subject-type "综合" --year 2025 --major "计算机"
```

可选参数：

- `--group-code`：指定专业组代码。
- `--major`：目标专业，用于判断组内目标专业占比。
- `--province`、`--subject-type`、`--year`：限定招生上下文。

重点看：这是风险初筛，不是真实调剂概率，也不是真实分流比例。

## 20. `comparison_query`

用途：做学校、专业、学校-专业方案的结构化并列对比。

学校对比推荐命令：

```powershell
python scripts/retrieval_tools.py comparison_query --target-type school --target "杭州电子科技大学" --target "浙江大学" --dimension school_profile --dimension admission --limit 5
```

学校 + 专业方案对比：

```powershell
python scripts/retrieval_tools.py comparison_query --target-type school_major --target "杭州电子科技大学" --target "浙江工业大学" --major "计算机科学与技术" --province "浙江" --subject-type "综合" --year 2025 --dimension school_major_profile --dimension admission --limit 5
```

可选参数：

- `--target-type`：`school`、`major`、`school_major`。
- `--target`：至少传两个；每个对象重复一次 `--target`。
- `--dimension`：可重复传入，例如 `school_profile`、`admission`、`market_reference`。
- `--major`、`--province`、`--subject-type`、`--score`、`--rank`、`--year`：给方案对比补上下文。
- `--limit`：每个维度返回数量，默认 10。

重点看：对比工具只做并列证据，不替用户下最终选择。

## 21. `major_streaming_policy_lookup`

用途：查询大类/专业分流政策和比例缺口。

推荐命令：

```powershell
python scripts/retrieval_tools.py major_streaming_policy_lookup --school "浙江大学" --major "计算机科学与技术" --province "浙江" --year 2025 --limit 10
```

可选参数：

- `--major`：目标专业。
- `--province`、`--year`：限定上下文。
- `--limit`：返回数量，默认 10。

重点看：当前是保守接口，通常会返回 `partial` 和真实分流比例缺口。

## 22. `civil_service_mapping`

用途：专业到考公岗位映射线索。

推荐命令：

```powershell
python scripts/retrieval_tools.py civil_service_mapping --major "计算机科学与技术" --year 2026 --limit 10
```

可选参数：

- `--province`：限定岗位省份。
- `--year`：岗位年份。
- `--limit`：返回数量，默认 20。

重点看：这是岗位文本命中和映射线索，不是正式可报判定。

## 23. `policy_rule_lookup`

用途：招生章程、单科限制、身体条件、语种限制等规则缺口查询。

推荐命令：

```powershell
python scripts/retrieval_tools.py policy_rule_lookup --school "杭州电子科技大学" --policy-type "单科限制" --province "浙江" --year 2025
```

可选参数：

- `--policy-type`：例如 `招生章程`、`单科限制`、`外语语种`、`身体条件`、`调剂规则`。
- `--province`、`--year`：限定上下文。

重点看：无官方来源时只能返回缺口，不能编规则。

## 24. `admission_history`

用途：查询历年录取分和位次。

推荐命令：

```powershell
python scripts/retrieval_tools.py admission_history --school "杭州电子科技大学" --major "计算机科学与技术" --province "浙江" --subject-type "综合" --years 2025 2024 2023 --limit 20
```

可选参数：

- `--school`：学校筛选。
- `--major`：专业筛选。
- `--province`：招生省份。
- `--subject-type`：科类。
- `--years 2025 2024`：年份列表。
- `--limit`：返回数量，默认 50。

重点看：历史录取只能作为参考，不保证未来录取。

## 25. `major_market_reference`

用途：查询专业通用市场样本。

推荐命令：

```powershell
python scripts/retrieval_tools.py major_market_reference --major "计算机科学与技术" --sample-limit 10
```

可选参数：

- `--sample-limit`：岗位样本数量，默认 10。

重点看：第三方招聘/薪资样本不是学校官方就业质量数据。

## 26. `civil_service_role_search`

用途：查询考公岗位文本命中样本。

推荐命令：

```powershell
python scripts/retrieval_tools.py civil_service_role_search --major "计算机科学与技术" --year 2026 --limit 10
```

可选参数：

- `--province`：岗位省份。
- `--year`：岗位年份。
- `--limit`：返回数量，默认 20。

重点看：岗位文本命中不等于该专业一定可报。

## 27. `data_gap_detection`

用途：按问题类型检测当前本地库还缺哪些数据。

推荐命令：

```powershell
python scripts/retrieval_tools.py data_gap_detection --question-type school_major_profile --available-fields school_basic major_basic school_major subject_eval
```

可选参数：

- `--question-type`：例如 `school_major_profile`、`major_market_reference`、`civil_service_role_search`、`comparison_query`、`major_streaming_policy_lookup`、`civil_service_mapping`、`policy_rule_lookup`。
- `--available-fields`：已经具备的字段列表，用空格分隔；不传时会列出该问题类型下的全部缺口。

重点看：缺口检测只描述当前本地库无法支撑的回答边界。

## 一次性验证建议

如果不想逐条命令跑，可以先跑抽样 smoke：

```powershell
python scripts/run_retrieval_smoke_cases.py --sample-per-tool 1 --report reports/retrieval_smoke_sample_27_tools.json
```

如果要完整验收 27 个工具的真实库结构稳定性：

```powershell
python scripts/run_retrieval_smoke_cases.py --report reports/retrieval_smoke_27_tools_full.json --timeout 60
```

当前最近一次完整结果是：305 个用例全部结构通过，质量提示 0 个。
