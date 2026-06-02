# 检索工具广覆盖测试命令数据集

生成时间：2026-05-21

用途：基于 `retrieval-tool-manual-test-commands.md` 的 27 个底层检索工具，扩展一组更贴近高考志愿填报真实问题的人工测试命令。该数据集侧重覆盖面，不要求每条都返回 `ok`；`partial`、`not_found`、`needs_clarification` 在缺数据、口径不完整或输入模糊时也可能是正确结果。

## 使用前置条件

```powershell
$env:GAOKAO_DB_HOST = "127.0.0.1"
$env:GAOKAO_DB_PORT = "3306"
$env:GAOKAO_DB_USER = "root"
$env:GAOKAO_DB_NAME = "gaokao_test_local"
$env:GAOKAO_DB_PASSWORD = "<你的本地密码>"
```

通用结构检查：

```powershell
python scripts/retrieval_function_registry.py list-names
python scripts/run_retrieval_smoke_cases.py --sample-per-tool 1 --report reports/retrieval_smoke_sample_27_tools.json
```

## 覆盖维度

- 输入形态：学校全称、简称、代码；专业全称、简称、专业代码；模糊词；不存在或极少见组合。
- 地域范围：浙江、江苏、上海、广东、山东、河南、四川、湖北、北京、天津等常见报考地域。
- 科类范围：综合、物理、历史；同时覆盖新高考与传统表述边界。
- 年份范围：2026 岗位样本、2025 当年上下文、2024/2023 历史参考。
- 志愿问题：学校识别、专业识别、院校画像、专业画像、分数位次、冲稳保、专业组、选科、招生计划、录取历史、费用校区、转专业、大类分流、政策规则、就业、薪资市场、考公、对比、数据缺口。

## A. 实体归一与别名识别

重点看 `normalized_slots`、`source_tables`、短简称是否走 `entity_aliases`，代码输入是否能归一到标准实体。

```powershell
python scripts/retrieval_tools.py school_lookup --school "杭电"
python scripts/retrieval_tools.py school_lookup --school "杭州电子科技大学"
python scripts/retrieval_tools.py school_lookup --school "10336"
python scripts/retrieval_tools.py school_lookup --school "浙大"
python scripts/retrieval_tools.py school_lookup --school "浙江大学"
python scripts/retrieval_tools.py school_lookup --school "10248"
python scripts/retrieval_tools.py school_lookup --school "南航"
python scripts/retrieval_tools.py school_lookup --school "南京航空航天大学"
python scripts/retrieval_tools.py school_lookup --school "华科"
python scripts/retrieval_tools.py school_lookup --school "华中科技大学"
python scripts/retrieval_tools.py school_lookup --school "上交"
python scripts/retrieval_tools.py school_lookup --school "上海交通大学"
python scripts/retrieval_tools.py major_lookup --major "计科"
python scripts/retrieval_tools.py major_lookup --major "计算机科学与技术"
python scripts/retrieval_tools.py major_lookup --major "080901"
python scripts/retrieval_tools.py major_lookup --major "软工"
python scripts/retrieval_tools.py major_lookup --major "软件工程"
python scripts/retrieval_tools.py major_lookup --major "080902"
python scripts/retrieval_tools.py major_lookup --major "电气"
python scripts/retrieval_tools.py major_lookup --major "电气工程及其自动化"
python scripts/retrieval_tools.py major_lookup --major "临床"
python scripts/retrieval_tools.py major_lookup --major "临床医学"
python scripts/retrieval_tools.py major_lookup --major "法学"
python scripts/retrieval_tools.py major_lookup --major "会计学"
```

## B. 学校画像与专业通用画像

重点看学校级、专业通用级口径是否被清楚标注，学校级就业不能被误当作某专业就业。

```powershell
python scripts/retrieval_tools.py school_profile --school "杭州电子科技大学"
python scripts/retrieval_tools.py school_profile --school "浙江大学"
python scripts/retrieval_tools.py school_profile --school "浙江工业大学"
python scripts/retrieval_tools.py school_profile --school "南京航空航天大学"
python scripts/retrieval_tools.py school_profile --school "上海交通大学"
python scripts/retrieval_tools.py school_profile --school "华中科技大学"
python scripts/retrieval_tools.py school_profile --school "深圳大学"
python scripts/retrieval_tools.py school_profile --school "西南交通大学"
python scripts/retrieval_tools.py major_profile --major "计算机科学与技术"
python scripts/retrieval_tools.py major_profile --major "软件工程"
python scripts/retrieval_tools.py major_profile --major "人工智能"
python scripts/retrieval_tools.py major_profile --major "数据科学与大数据技术"
python scripts/retrieval_tools.py major_profile --major "电子信息工程"
python scripts/retrieval_tools.py major_profile --major "自动化"
python scripts/retrieval_tools.py major_profile --major "电气工程及其自动化"
python scripts/retrieval_tools.py major_profile --major "临床医学"
python scripts/retrieval_tools.py major_profile --major "口腔医学"
python scripts/retrieval_tools.py major_profile --major "法学"
python scripts/retrieval_tools.py major_profile --major "汉语言文学"
python scripts/retrieval_tools.py major_profile --major "会计学"
```

## C. 开设专业与开设学校列表

重点看“学校开设专业”“开设该专业的学校”是否与“某省某年招生计划”区分清楚。

```powershell
python scripts/retrieval_tools.py school_major_list --school "杭州电子科技大学" --major-category "计算机类" --limit 30
python scripts/retrieval_tools.py school_major_list --school "杭州电子科技大学" --major-category "电子信息类" --limit 30
python scripts/retrieval_tools.py school_major_list --school "浙江大学" --major-category "工学" --limit 50
python scripts/retrieval_tools.py school_major_list --school "浙江大学" --major-category "医学" --limit 50
python scripts/retrieval_tools.py school_major_list --school "南京航空航天大学" --major-category "航空航天类" --limit 30
python scripts/retrieval_tools.py school_major_list --school "上海交通大学" --major-category "计算机类" --limit 30
python scripts/retrieval_tools.py school_major_list --school "华中科技大学" --major-category "临床医学类" --limit 30
python scripts/retrieval_tools.py school_major_list --school "深圳大学" --major-category "经济学" --limit 30
python scripts/retrieval_tools.py major_school_list --major "计算机科学与技术" --province-filter "浙江" --school-level-filter "本科" --limit 30
python scripts/retrieval_tools.py major_school_list --major "软件工程" --province-filter "江苏" --school-level-filter "本科" --limit 30
python scripts/retrieval_tools.py major_school_list --major "人工智能" --province-filter "上海" --school-level-filter "本科" --limit 30
python scripts/retrieval_tools.py major_school_list --major "电气工程及其自动化" --province-filter "湖北" --school-level-filter "本科" --limit 30
python scripts/retrieval_tools.py major_school_list --major "临床医学" --province-filter "浙江" --school-level-filter "本科" --limit 30
python scripts/retrieval_tools.py major_school_list --major "口腔医学" --province-filter "四川" --school-level-filter "本科" --limit 30
python scripts/retrieval_tools.py major_school_list --major "法学" --province-filter "北京" --school-level-filter "本科" --limit 30
python scripts/retrieval_tools.py major_school_list --major "会计学" --province-filter "广东" --school-level-filter "本科" --limit 30
```

## D. 分数转位次与冲稳保学校匹配

重点看分数换位次是否严格限定同省、同科类、同年份；冲稳保只能作为历史位次参考。

```powershell
python scripts/retrieval_tools.py score_to_rank --province "浙江" --subject-type "综合" --score 620 --year 2025
python scripts/retrieval_tools.py score_to_rank --province "浙江" --subject-type "综合" --score 580 --year 2025
python scripts/retrieval_tools.py score_to_rank --province "广东" --subject-type "物理" --score 620 --year 2025
python scripts/retrieval_tools.py score_to_rank --province "广东" --subject-type "历史" --score 560 --year 2025
python scripts/retrieval_tools.py score_to_rank --province "江苏" --subject-type "物理" --score 610 --year 2025
python scripts/retrieval_tools.py score_to_rank --province "江苏" --subject-type "历史" --score 590 --year 2025
python scripts/retrieval_tools.py score_to_rank --province "山东" --subject-type "综合" --score 600 --year 2025
python scripts/retrieval_tools.py score_to_rank --province "河南" --subject-type "理科" --score 590 --year 2025
python scripts/retrieval_tools.py rank_to_school_match --province "浙江" --subject-type "综合" --score 620 --year 2025 --preferred-regions 浙江 江苏 上海 --limit 30
python scripts/retrieval_tools.py rank_to_school_match --province "浙江" --subject-type "综合" --rank 25000 --year 2025 --reference-years 2024 2023 --preferred-regions 浙江 江苏 上海 --limit 30
python scripts/retrieval_tools.py rank_to_school_match --province "广东" --subject-type "物理" --score 610 --year 2025 --preferred-regions 广东 福建 湖南 --limit 30
python scripts/retrieval_tools.py rank_to_school_match --province "广东" --subject-type "历史" --rank 18000 --year 2025 --reference-years 2024 2023 --preferred-regions 广东 上海 北京 --limit 30
python scripts/retrieval_tools.py rank_to_school_match --province "江苏" --subject-type "物理" --score 615 --year 2025 --school-level-filter "双一流" --limit 30
python scripts/retrieval_tools.py rank_to_school_match --province "山东" --subject-type "综合" --rank 45000 --year 2025 --preferred-regions 山东 江苏 天津 --limit 30
python scripts/retrieval_tools.py rank_to_school_match --province "河南" --subject-type "理科" --score 600 --year 2025 --preferred-regions 河南 湖北 陕西 --limit 30
python scripts/retrieval_tools.py rank_to_school_match --province "四川" --subject-type "理科" --rank 30000 --year 2025 --school-level-filter "本科" --limit 30
```

## E. 分数位次到学校-专业匹配

重点看是否返回学校-专业行，专业大类、试验班、方向名是否通过 `warnings` 提示。

```powershell
python scripts/retrieval_tools.py rank_to_major_match --province "浙江" --major "计算机" --subject-type "综合" --score 620 --year 2025 --preferred-regions 浙江 江苏 上海 --limit 30
python scripts/retrieval_tools.py rank_to_major_match --province "浙江" --major "软件工程" --subject-type "综合" --rank 26000 --year 2025 --reference-years 2024 2023 --limit 30
python scripts/retrieval_tools.py rank_to_major_match --province "浙江" --major "电子信息" --subject-type "综合" --score 610 --year 2025 --preferred-regions 浙江 江苏 上海 --limit 30
python scripts/retrieval_tools.py rank_to_major_match --province "广东" --major "计算机" --subject-type "物理" --score 610 --year 2025 --preferred-regions 广东 福建 湖南 --limit 30
python scripts/retrieval_tools.py rank_to_major_match --province "广东" --major "法学" --subject-type "历史" --rank 12000 --year 2025 --preferred-regions 广东 北京 上海 --limit 30
python scripts/retrieval_tools.py rank_to_major_match --province "江苏" --major "临床医学" --subject-type "物理" --score 630 --year 2025 --preferred-regions 江苏 浙江 上海 --limit 30
python scripts/retrieval_tools.py rank_to_major_match --province "山东" --major "电气工程及其自动化" --subject-type "综合" --rank 35000 --year 2025 --preferred-regions 山东 江苏 天津 --limit 30
python scripts/retrieval_tools.py rank_to_major_match --province "四川" --major "口腔医学" --subject-type "理科" --rank 12000 --year 2025 --preferred-regions 四川 重庆 陕西 --limit 30
python scripts/retrieval_tools.py rank_to_major_match --province "河南" --major "会计学" --subject-type "文科" --score 570 --year 2025 --school-level-filter "本科" --limit 30
python scripts/retrieval_tools.py rank_to_major_match --province "湖北" --major "人工智能" --subject-type "物理" --score 600 --year 2025 --preferred-regions 湖北 湖南 广东 --limit 30
```

## F. 校专业画像与专业组

重点看学校级、专业通用级、校专业级、招生专业组级口径能否分开；缺少校专业就业、薪资、官网介绍时应返回 `partial` 和 `data_gaps`。

```powershell
python scripts/retrieval_tools.py school_major_profile --school "杭州电子科技大学" --major "计算机科学与技术" --province "浙江" --subject-type "综合" --year 2025
python scripts/retrieval_tools.py school_major_profile --school "杭州电子科技大学" --major "软件工程" --province "浙江" --subject-type "综合" --year 2025
python scripts/retrieval_tools.py school_major_profile --school "浙江大学" --major "计算机科学与技术" --province "浙江" --subject-type "综合" --year 2025
python scripts/retrieval_tools.py school_major_profile --school "浙江工业大学" --major "电气工程及其自动化" --province "浙江" --subject-type "综合" --year 2025
python scripts/retrieval_tools.py school_major_profile --school "南京航空航天大学" --major "飞行器设计与工程" --province "江苏" --subject-type "物理" --year 2025
python scripts/retrieval_tools.py school_major_profile --school "华中科技大学" --major "临床医学" --province "湖北" --subject-type "物理" --year 2025
python scripts/retrieval_tools.py specialty_group_lookup --school "杭州电子科技大学" --major "计算机" --province "浙江" --subject-type "综合" --year 2025 --limit 20
python scripts/retrieval_tools.py specialty_group_lookup --school "浙江大学" --major "工科试验班" --province "浙江" --subject-type "综合" --year 2025 --limit 20
python scripts/retrieval_tools.py specialty_group_lookup --school "浙江工业大学" --major "电气" --province "浙江" --subject-type "综合" --year 2025 --limit 20
python scripts/retrieval_tools.py specialty_group_lookup --school "南京航空航天大学" --major "航空航天" --province "江苏" --subject-type "物理" --year 2025 --limit 20
python scripts/retrieval_tools.py specialty_group_lookup --school "上海交通大学" --major "电子信息" --province "上海" --subject-type "综合" --year 2025 --limit 20
python scripts/retrieval_tools.py specialty_group_lookup --school "华中科技大学" --major "临床医学" --province "湖北" --subject-type "物理" --year 2025 --limit 20
```

## G. 选科要求、专业组风险与院系专业

重点看选科要求按省份和年份解释；专业组风险只做初筛，不是真实调剂概率；院系关系不等于招生计划。

```powershell
python scripts/retrieval_tools.py subject_requirement_lookup --major "计算机科学与技术" --school "杭州电子科技大学" --province "浙江" --subject-type "综合" --year 2025 --limit 30
python scripts/retrieval_tools.py subject_requirement_lookup --major "软件工程" --school "浙江工业大学" --province "浙江" --subject-type "综合" --year 2025 --limit 30
python scripts/retrieval_tools.py subject_requirement_lookup --major "临床医学" --school "华中科技大学" --province "湖北" --subject-type "物理" --year 2025 --limit 30
python scripts/retrieval_tools.py subject_requirement_lookup --major "法学" --province "广东" --subject-type "历史" --year 2025 --limit 30
python scripts/retrieval_tools.py subject_requirement_lookup --major "会计学" --province "山东" --subject-type "综合" --year 2025 --limit 30
python scripts/retrieval_tools.py specialty_group_risk --school "杭州电子科技大学" --province "浙江" --subject-type "综合" --year 2025 --major "计算机"
python scripts/retrieval_tools.py specialty_group_risk --school "浙江大学" --province "浙江" --subject-type "综合" --year 2025 --major "计算机科学与技术"
python scripts/retrieval_tools.py specialty_group_risk --school "浙江工业大学" --province "浙江" --subject-type "综合" --year 2025 --major "电气工程及其自动化"
python scripts/retrieval_tools.py specialty_group_risk --school "上海交通大学" --province "上海" --subject-type "综合" --year 2025 --major "电子信息"
python scripts/retrieval_tools.py specialty_group_risk --school "华中科技大学" --province "湖北" --subject-type "物理" --year 2025 --major "临床医学"
python scripts/retrieval_tools.py school_department_major_list --school "杭州电子科技大学" --department "计算机" --limit 50
python scripts/retrieval_tools.py school_department_major_list --school "杭州电子科技大学" --major "软件工程" --limit 50
python scripts/retrieval_tools.py school_department_major_list --school "浙江大学" --department "信息" --limit 50
python scripts/retrieval_tools.py school_department_major_list --school "浙江大学" --major "临床医学" --limit 50
python scripts/retrieval_tools.py school_department_major_list --school "南京航空航天大学" --department "航空" --limit 50
python scripts/retrieval_tools.py school_department_major_list --school "华中科技大学" --department "医学" --limit 50
```

## H. 招生计划与录取历史

重点看计划数不等于录取人数；历史录取只能作为参考，不保证未来录取。

```powershell
python scripts/retrieval_tools.py plan_history --school "杭州电子科技大学" --major "计算机科学与技术" --province "浙江" --years 2025 2024 2023 --limit 50
python scripts/retrieval_tools.py plan_history --school "杭州电子科技大学" --major "软件工程" --province "浙江" --years 2025 2024 2023 --limit 50
python scripts/retrieval_tools.py plan_history --school "浙江大学" --major "工科试验班" --province "浙江" --years 2025 2024 2023 --limit 50
python scripts/retrieval_tools.py plan_history --school "浙江工业大学" --major "电气工程及其自动化" --province "浙江" --years 2025 2024 2023 --limit 50
python scripts/retrieval_tools.py plan_history --school "南京航空航天大学" --major "航空航天类" --province "江苏" --years 2025 2024 2023 --limit 50
python scripts/retrieval_tools.py plan_history --school "华中科技大学" --major "临床医学" --province "湖北" --years 2025 2024 2023 --limit 50
python scripts/retrieval_tools.py plan_history --school "深圳大学" --major "计算机科学与技术" --province "广东" --years 2025 2024 2023 --limit 50
python scripts/retrieval_tools.py admission_history --school "杭州电子科技大学" --major "计算机科学与技术" --province "浙江" --subject-type "综合" --years 2025 2024 2023 --limit 50
python scripts/retrieval_tools.py admission_history --school "杭州电子科技大学" --major "软件工程" --province "浙江" --subject-type "综合" --years 2025 2024 2023 --limit 50
python scripts/retrieval_tools.py admission_history --school "浙江大学" --major "计算机科学与技术" --province "浙江" --subject-type "综合" --years 2025 2024 2023 --limit 50
python scripts/retrieval_tools.py admission_history --school "浙江工业大学" --major "电气工程及其自动化" --province "浙江" --subject-type "综合" --years 2025 2024 2023 --limit 50
python scripts/retrieval_tools.py admission_history --school "南京航空航天大学" --major "飞行器设计与工程" --province "江苏" --subject-type "物理" --years 2025 2024 2023 --limit 50
python scripts/retrieval_tools.py admission_history --school "华中科技大学" --major "临床医学" --province "湖北" --subject-type "物理" --years 2025 2024 2023 --limit 50
python scripts/retrieval_tools.py admission_history --school "深圳大学" --major "法学" --province "广东" --subject-type "历史" --years 2025 2024 2023 --limit 50
```

## I. 费用校区、转专业、大类分流与政策规则

重点看无官方来源时是否明确返回缺口，不能推测校区、转专业成功率、分流比例或政策限制。

```powershell
python scripts/retrieval_tools.py fee_and_campus_lookup --school "杭州电子科技大学" --major "计算机科学与技术" --province "浙江" --year 2025 --limit 30
python scripts/retrieval_tools.py fee_and_campus_lookup --school "浙江大学" --major "工科试验班" --province "浙江" --year 2025 --limit 30
python scripts/retrieval_tools.py fee_and_campus_lookup --school "浙江工业大学" --major "电气工程及其自动化" --province "浙江" --year 2025 --limit 30
python scripts/retrieval_tools.py fee_and_campus_lookup --school "南京航空航天大学" --major "航空航天类" --province "江苏" --year 2025 --limit 30
python scripts/retrieval_tools.py fee_and_campus_lookup --school "深圳大学" --major "计算机科学与技术" --province "广东" --year 2025 --limit 30
python scripts/retrieval_tools.py transfer_policy_lookup --school "杭州电子科技大学"
python scripts/retrieval_tools.py transfer_policy_lookup --school "浙江大学"
python scripts/retrieval_tools.py transfer_policy_lookup --school "浙江工业大学"
python scripts/retrieval_tools.py transfer_policy_lookup --school "南京航空航天大学"
python scripts/retrieval_tools.py transfer_policy_lookup --school "深圳大学"
python scripts/retrieval_tools.py major_streaming_policy_lookup --school "浙江大学" --major "计算机科学与技术" --province "浙江" --year 2025 --limit 20
python scripts/retrieval_tools.py major_streaming_policy_lookup --school "浙江大学" --major "工科试验班" --province "浙江" --year 2025 --limit 20
python scripts/retrieval_tools.py major_streaming_policy_lookup --school "上海交通大学" --major "电子信息类" --province "上海" --year 2025 --limit 20
python scripts/retrieval_tools.py major_streaming_policy_lookup --school "南京航空航天大学" --major "航空航天类" --province "江苏" --year 2025 --limit 20
python scripts/retrieval_tools.py policy_rule_lookup --school "杭州电子科技大学" --policy-type "招生章程" --province "浙江" --year 2025
python scripts/retrieval_tools.py policy_rule_lookup --school "杭州电子科技大学" --policy-type "单科限制" --province "浙江" --year 2025
python scripts/retrieval_tools.py policy_rule_lookup --school "浙江大学" --policy-type "外语语种" --province "浙江" --year 2025
python scripts/retrieval_tools.py policy_rule_lookup --school "华中科技大学" --policy-type "身体条件" --province "湖北" --year 2025
python scripts/retrieval_tools.py policy_rule_lookup --school "南京航空航天大学" --policy-type "调剂规则" --province "江苏" --year 2025
python scripts/retrieval_tools.py policy_rule_lookup --school "深圳大学" --policy-type "中外合作" --province "广东" --year 2025
```

## J. 就业、市场样本与考公线索

重点看学校级就业、专业通用市场样本、岗位文本命中三者不能互相替代。

```powershell
python scripts/retrieval_tools.py employment_summary --school "杭州电子科技大学" --limit 5
python scripts/retrieval_tools.py employment_summary --school "浙江大学" --limit 5
python scripts/retrieval_tools.py employment_summary --school "浙江工业大学" --limit 5
python scripts/retrieval_tools.py employment_summary --school "南京航空航天大学" --limit 5
python scripts/retrieval_tools.py employment_summary --school "华中科技大学" --limit 5
python scripts/retrieval_tools.py employment_summary --school "深圳大学" --limit 5
python scripts/retrieval_tools.py major_market_reference --major "计算机科学与技术" --sample-limit 20
python scripts/retrieval_tools.py major_market_reference --major "软件工程" --sample-limit 20
python scripts/retrieval_tools.py major_market_reference --major "人工智能" --sample-limit 20
python scripts/retrieval_tools.py major_market_reference --major "数据科学与大数据技术" --sample-limit 20
python scripts/retrieval_tools.py major_market_reference --major "电气工程及其自动化" --sample-limit 20
python scripts/retrieval_tools.py major_market_reference --major "临床医学" --sample-limit 20
python scripts/retrieval_tools.py major_market_reference --major "法学" --sample-limit 20
python scripts/retrieval_tools.py civil_service_mapping --major "计算机科学与技术" --year 2026 --limit 20
python scripts/retrieval_tools.py civil_service_mapping --major "软件工程" --year 2026 --limit 20
python scripts/retrieval_tools.py civil_service_mapping --major "法学" --year 2026 --limit 20
python scripts/retrieval_tools.py civil_service_mapping --major "会计学" --year 2026 --limit 20
python scripts/retrieval_tools.py civil_service_mapping --major "汉语言文学" --year 2026 --limit 20
python scripts/retrieval_tools.py civil_service_mapping --major "临床医学" --year 2026 --limit 20
python scripts/retrieval_tools.py civil_service_role_search --major "计算机科学与技术" --year 2026 --limit 20
python scripts/retrieval_tools.py civil_service_role_search --major "计算机科学与技术" --province "浙江" --year 2026 --limit 20
python scripts/retrieval_tools.py civil_service_role_search --major "软件工程" --province "广东" --year 2026 --limit 20
python scripts/retrieval_tools.py civil_service_role_search --major "法学" --province "北京" --year 2026 --limit 20
python scripts/retrieval_tools.py civil_service_role_search --major "会计学" --province "江苏" --year 2026 --limit 20
python scripts/retrieval_tools.py civil_service_role_search --major "汉语言文学" --province "山东" --year 2026 --limit 20
```

## K. 结构化对比

重点看对比工具是否只输出并列证据，不替用户做最终选择。

```powershell
python scripts/retrieval_tools.py comparison_query --target-type school --target "杭州电子科技大学" --target "浙江工业大学" --dimension school_profile --dimension admission --limit 10
python scripts/retrieval_tools.py comparison_query --target-type school --target "浙江大学" --target "上海交通大学" --dimension school_profile --dimension admission --dimension market_reference --limit 10
python scripts/retrieval_tools.py comparison_query --target-type school --target "南京航空航天大学" --target "西南交通大学" --dimension school_profile --dimension admission --limit 10
python scripts/retrieval_tools.py comparison_query --target-type school --target "深圳大学" --target "华南理工大学" --dimension school_profile --dimension admission --limit 10
python scripts/retrieval_tools.py comparison_query --target-type major --target "计算机科学与技术" --target "软件工程" --dimension major_profile --dimension market_reference --limit 10
python scripts/retrieval_tools.py comparison_query --target-type major --target "人工智能" --target "数据科学与大数据技术" --dimension major_profile --dimension market_reference --dimension civil_service --limit 10
python scripts/retrieval_tools.py comparison_query --target-type major --target "法学" --target "会计学" --dimension major_profile --dimension market_reference --dimension civil_service --limit 10
python scripts/retrieval_tools.py comparison_query --target-type school_major --target "杭州电子科技大学" --target "浙江工业大学" --major "计算机科学与技术" --province "浙江" --subject-type "综合" --year 2025 --dimension school_major_profile --dimension admission --dimension market_reference --limit 10
python scripts/retrieval_tools.py comparison_query --target-type school_major --target "浙江大学" --target "上海交通大学" --major "电子信息类" --province "浙江" --subject-type "综合" --year 2025 --dimension school_major_profile --dimension admission --limit 10
python scripts/retrieval_tools.py comparison_query --target-type school_major --target "华中科技大学" --target "中南大学" --major "临床医学" --province "湖北" --subject-type "物理" --year 2025 --dimension school_major_profile --dimension admission --limit 10
python scripts/retrieval_tools.py comparison_query --target-type school_major --target "南京航空航天大学" --target "北京航空航天大学" --major "航空航天类" --province "江苏" --subject-type "物理" --year 2025 --dimension school_major_profile --dimension admission --limit 10
```

## L. 来源追踪与数据缺口

重点看 `source_tables`、`scope_notes`、`reliability` 和缺口边界是否明确。

```powershell
python scripts/retrieval_tools.py source_trace_lookup
python scripts/retrieval_tools.py source_trace_lookup --tool-name school_lookup
python scripts/retrieval_tools.py source_trace_lookup --tool-name major_lookup
python scripts/retrieval_tools.py source_trace_lookup --tool-name school_major_profile
python scripts/retrieval_tools.py source_trace_lookup --tool-name rank_to_major_match
python scripts/retrieval_tools.py source_trace_lookup --tool-name specialty_group_risk
python scripts/retrieval_tools.py source_trace_lookup --tool-name major_streaming_policy_lookup
python scripts/retrieval_tools.py source_trace_lookup --tool-name civil_service_mapping
python scripts/retrieval_tools.py source_trace_lookup --tool-name policy_rule_lookup
python scripts/retrieval_tools.py source_trace_lookup --tool-name major_market_reference
python scripts/retrieval_tools.py data_gap_detection --question-type school_major_profile --available-fields school_basic major_basic school_major subject_eval
python scripts/retrieval_tools.py data_gap_detection --question-type school_major_profile --available-fields school_basic major_basic
python scripts/retrieval_tools.py data_gap_detection --question-type major_market_reference --available-fields major_basic job_samples
python scripts/retrieval_tools.py data_gap_detection --question-type civil_service_role_search --available-fields major_basic civil_service_roles
python scripts/retrieval_tools.py data_gap_detection --question-type comparison_query --available-fields school_basic major_basic admission_history
python scripts/retrieval_tools.py data_gap_detection --question-type major_streaming_policy_lookup --available-fields school_basic major_basic plan_history
python scripts/retrieval_tools.py data_gap_detection --question-type civil_service_mapping --available-fields major_basic
python scripts/retrieval_tools.py data_gap_detection --question-type policy_rule_lookup --available-fields school_basic
python scripts/retrieval_tools.py data_gap_detection --question-type school_major_profile
python scripts/retrieval_tools.py data_gap_detection --question-type policy_rule_lookup
```

## M. 模糊、缺失与边界输入

这些命令用于验证工具是否能稳妥返回 `needs_clarification`、`not_found` 或 `partial`，而不是猜测或编造。

```powershell
python scripts/retrieval_tools.py school_lookup --school "华大"
python scripts/retrieval_tools.py school_lookup --school "电子科技大学"
python scripts/retrieval_tools.py school_lookup --school "不存在大学测试样本"
python scripts/retrieval_tools.py major_lookup --major "智能"
python scripts/retrieval_tools.py major_lookup --major "工程"
python scripts/retrieval_tools.py major_lookup --major "不存在专业测试样本"
python scripts/retrieval_tools.py school_profile --school "不存在大学测试样本"
python scripts/retrieval_tools.py major_profile --major "不存在专业测试样本"
python scripts/retrieval_tools.py school_major_profile --school "杭州电子科技大学" --major "临床医学" --province "浙江" --subject-type "综合" --year 2025
python scripts/retrieval_tools.py school_major_profile --school "浙江大学" --major "飞行器设计与工程" --province "浙江" --subject-type "综合" --year 2025
python scripts/retrieval_tools.py score_to_rank --province "浙江" --subject-type "历史" --score 620 --year 2025
python scripts/retrieval_tools.py score_to_rank --province "浙江" --subject-type "综合" --score 900 --year 2025
python scripts/retrieval_tools.py rank_to_school_match --province "浙江" --subject-type "综合" --score 1 --year 2025 --limit 10
python scripts/retrieval_tools.py rank_to_major_match --province "浙江" --major "计算机" --subject-type "综合" --score 1 --year 2025 --limit 10
python scripts/retrieval_tools.py specialty_group_lookup --school "杭州电子科技大学" --major "考古学" --province "浙江" --subject-type "综合" --year 2025 --limit 10
python scripts/retrieval_tools.py subject_requirement_lookup --major "考古学" --school "杭州电子科技大学" --province "浙江" --subject-type "综合" --year 2025 --limit 10
python scripts/retrieval_tools.py fee_and_campus_lookup --school "杭州电子科技大学" --major "考古学" --province "浙江" --year 2025 --limit 10
python scripts/retrieval_tools.py policy_rule_lookup --school "杭州电子科技大学" --policy-type "保研率" --province "浙江" --year 2025
python scripts/retrieval_tools.py civil_service_mapping --major "不存在专业测试样本" --year 2026 --limit 10
python scripts/retrieval_tools.py data_gap_detection --question-type unknown_question_type
```

## N. 高频志愿问题组合套件

下面按真实用户问题组织，适合人工逐组跑完后检查回答链路是否能拼成可靠建议。

### N1. “浙江 620 分综合，想读计算机，怎么冲稳保？”

```powershell
python scripts/retrieval_tools.py score_to_rank --province "浙江" --subject-type "综合" --score 620 --year 2025
python scripts/retrieval_tools.py rank_to_school_match --province "浙江" --subject-type "综合" --score 620 --year 2025 --preferred-regions 浙江 江苏 上海 --limit 30
python scripts/retrieval_tools.py rank_to_major_match --province "浙江" --major "计算机" --subject-type "综合" --score 620 --year 2025 --preferred-regions 浙江 江苏 上海 --limit 30
python scripts/retrieval_tools.py subject_requirement_lookup --major "计算机科学与技术" --province "浙江" --subject-type "综合" --year 2025 --limit 30
python scripts/retrieval_tools.py data_gap_detection --question-type comparison_query --available-fields school_basic major_basic admission_history
```

### N2. “杭电计算机值不值得报？”

```powershell
python scripts/retrieval_tools.py school_lookup --school "杭电"
python scripts/retrieval_tools.py major_lookup --major "计科"
python scripts/retrieval_tools.py school_major_profile --school "杭州电子科技大学" --major "计算机科学与技术" --province "浙江" --subject-type "综合" --year 2025
python scripts/retrieval_tools.py admission_history --school "杭州电子科技大学" --major "计算机科学与技术" --province "浙江" --subject-type "综合" --years 2025 2024 2023 --limit 30
python scripts/retrieval_tools.py plan_history --school "杭州电子科技大学" --major "计算机科学与技术" --province "浙江" --years 2025 2024 2023 --limit 30
python scripts/retrieval_tools.py fee_and_campus_lookup --school "杭州电子科技大学" --major "计算机科学与技术" --province "浙江" --year 2025 --limit 20
python scripts/retrieval_tools.py major_market_reference --major "计算机科学与技术" --sample-limit 20
```

### N3. “专业组里有不想去的专业，调剂风险大吗？”

```powershell
python scripts/retrieval_tools.py specialty_group_lookup --school "杭州电子科技大学" --major "计算机" --province "浙江" --subject-type "综合" --year 2025 --limit 20
python scripts/retrieval_tools.py specialty_group_risk --school "杭州电子科技大学" --province "浙江" --subject-type "综合" --year 2025 --major "计算机"
python scripts/retrieval_tools.py subject_requirement_lookup --major "计算机科学与技术" --school "杭州电子科技大学" --province "浙江" --subject-type "综合" --year 2025 --limit 20
python scripts/retrieval_tools.py policy_rule_lookup --school "杭州电子科技大学" --policy-type "调剂规则" --province "浙江" --year 2025
python scripts/retrieval_tools.py data_gap_detection --question-type school_major_profile --available-fields school_basic major_basic school_major subject_eval
```

### N4. “想转专业，哪些信息必须先查？”

```powershell
python scripts/retrieval_tools.py transfer_policy_lookup --school "杭州电子科技大学"
python scripts/retrieval_tools.py transfer_policy_lookup --school "浙江大学"
python scripts/retrieval_tools.py major_streaming_policy_lookup --school "浙江大学" --major "计算机科学与技术" --province "浙江" --year 2025 --limit 20
python scripts/retrieval_tools.py policy_rule_lookup --school "浙江大学" --policy-type "转专业" --province "浙江" --year 2025
python scripts/retrieval_tools.py data_gap_detection --question-type major_streaming_policy_lookup --available-fields school_basic major_basic plan_history
```

### N5. “计算机、软件、人工智能、大数据怎么选？”

```powershell
python scripts/retrieval_tools.py comparison_query --target-type major --target "计算机科学与技术" --target "软件工程" --dimension major_profile --dimension market_reference --dimension civil_service --limit 10
python scripts/retrieval_tools.py comparison_query --target-type major --target "人工智能" --target "数据科学与大数据技术" --dimension major_profile --dimension market_reference --dimension civil_service --limit 10
python scripts/retrieval_tools.py major_market_reference --major "计算机科学与技术" --sample-limit 20
python scripts/retrieval_tools.py major_market_reference --major "软件工程" --sample-limit 20
python scripts/retrieval_tools.py major_market_reference --major "人工智能" --sample-limit 20
python scripts/retrieval_tools.py major_market_reference --major "数据科学与大数据技术" --sample-limit 20
python scripts/retrieval_tools.py civil_service_mapping --major "计算机科学与技术" --year 2026 --limit 20
python scripts/retrieval_tools.py civil_service_mapping --major "软件工程" --year 2026 --limit 20
```

### N6. “将来想考公，专业怎么选？”

```powershell
python scripts/retrieval_tools.py civil_service_mapping --major "法学" --year 2026 --limit 20
python scripts/retrieval_tools.py civil_service_mapping --major "汉语言文学" --year 2026 --limit 20
python scripts/retrieval_tools.py civil_service_mapping --major "会计学" --year 2026 --limit 20
python scripts/retrieval_tools.py civil_service_mapping --major "计算机科学与技术" --year 2026 --limit 20
python scripts/retrieval_tools.py civil_service_role_search --major "法学" --province "浙江" --year 2026 --limit 20
python scripts/retrieval_tools.py civil_service_role_search --major "汉语言文学" --province "浙江" --year 2026 --limit 20
python scripts/retrieval_tools.py comparison_query --target-type major --target "法学" --target "汉语言文学" --dimension major_profile --dimension civil_service --limit 10
python scripts/retrieval_tools.py comparison_query --target-type major --target "会计学" --target "计算机科学与技术" --dimension major_profile --dimension civil_service --limit 10
```

## O. 建议抽样顺序

如果时间有限，建议优先跑：

```powershell
python scripts/retrieval_tools.py school_lookup --school "杭电"
python scripts/retrieval_tools.py major_lookup --major "计科"
python scripts/retrieval_tools.py score_to_rank --province "浙江" --subject-type "综合" --score 620 --year 2025
python scripts/retrieval_tools.py rank_to_major_match --province "浙江" --major "计算机" --subject-type "综合" --score 620 --year 2025 --preferred-regions 浙江 江苏 上海 --limit 30
python scripts/retrieval_tools.py school_major_profile --school "杭州电子科技大学" --major "计算机科学与技术" --province "浙江" --subject-type "综合" --year 2025
python scripts/retrieval_tools.py specialty_group_risk --school "杭州电子科技大学" --province "浙江" --subject-type "综合" --year 2025 --major "计算机"
python scripts/retrieval_tools.py admission_history --school "杭州电子科技大学" --major "计算机科学与技术" --province "浙江" --subject-type "综合" --years 2025 2024 2023 --limit 30
python scripts/retrieval_tools.py policy_rule_lookup --school "杭州电子科技大学" --policy-type "调剂规则" --province "浙江" --year 2025
python scripts/retrieval_tools.py major_market_reference --major "计算机科学与技术" --sample-limit 20
python scripts/retrieval_tools.py civil_service_mapping --major "计算机科学与技术" --year 2026 --limit 20
python scripts/retrieval_tools.py comparison_query --target-type school_major --target "杭州电子科技大学" --target "浙江工业大学" --major "计算机科学与技术" --province "浙江" --subject-type "综合" --year 2025 --dimension school_major_profile --dimension admission --dimension market_reference --limit 10
python scripts/retrieval_tools.py data_gap_detection --question-type school_major_profile --available-fields school_basic major_basic school_major subject_eval
```

## P. 二次审查补强结论

第一版已经覆盖 27 个工具，但为了更接近真实志愿填报问答，本轮补强增加以下覆盖：

- 人群与目标：高分冲名校、中高分选强专业、中分求稳、低分保本科、历史类/文科、物理类/理科、医学、师范、财经、法学、考公、预算敏感、城市优先、省内优先、就业优先、升学优先。
- 数据口径：学校级、专业通用级、校专业级、专业组级、招生计划、录取历史、选科要求、费用校区、政策规则、就业市场、考公岗位、缺口检测。
- 风险边界：模糊简称、同名学校歧义、专业大类与具体专业混用、试验班/基地班/中外合作/专项计划/师范方向/医学体检限制/语种限制/校区不稳定。
- 输入边界：只给位次、只给分数、缺少年份、缺少科类、极高分、极低分、不存在学校、不存在专业、错配学校专业、省份科类不匹配。

## Q. 工具级查缺补漏命令

这一组按工具补充“第一版较少触及”的别名、边界和宽泛查询。

```powershell
python scripts/retrieval_tools.py school_lookup --school "西电"
python scripts/retrieval_tools.py school_lookup --school "电子科技大学"
python scripts/retrieval_tools.py school_lookup --school "成电"
python scripts/retrieval_tools.py school_lookup --school "北邮"
python scripts/retrieval_tools.py school_lookup --school "北工大"
python scripts/retrieval_tools.py school_lookup --school "华师"
python scripts/retrieval_tools.py school_lookup --school "山大"
python scripts/retrieval_tools.py school_lookup --school "河大"
python scripts/retrieval_tools.py school_lookup --school "重邮"
python scripts/retrieval_tools.py school_lookup --school "南邮"
python scripts/retrieval_tools.py major_lookup --major "网安"
python scripts/retrieval_tools.py major_lookup --major "网络空间安全"
python scripts/retrieval_tools.py major_lookup --major "信息安全"
python scripts/retrieval_tools.py major_lookup --major "电子信息"
python scripts/retrieval_tools.py major_lookup --major "通信工程"
python scripts/retrieval_tools.py major_lookup --major "机器人工程"
python scripts/retrieval_tools.py major_lookup --major "车辆工程"
python scripts/retrieval_tools.py major_lookup --major "土木工程"
python scripts/retrieval_tools.py major_lookup --major "材料科学与工程"
python scripts/retrieval_tools.py major_lookup --major "生物医学工程"
python scripts/retrieval_tools.py school_profile --school "北京邮电大学"
python scripts/retrieval_tools.py school_profile --school "西安电子科技大学"
python scripts/retrieval_tools.py school_profile --school "电子科技大学"
python scripts/retrieval_tools.py school_profile --school "南京邮电大学"
python scripts/retrieval_tools.py school_profile --school "重庆邮电大学"
python scripts/retrieval_tools.py school_profile --school "北京工业大学"
python scripts/retrieval_tools.py major_profile --major "网络空间安全"
python scripts/retrieval_tools.py major_profile --major "信息安全"
python scripts/retrieval_tools.py major_profile --major "通信工程"
python scripts/retrieval_tools.py major_profile --major "机器人工程"
python scripts/retrieval_tools.py major_profile --major "车辆工程"
python scripts/retrieval_tools.py major_profile --major "土木工程"
python scripts/retrieval_tools.py major_profile --major "材料科学与工程"
python scripts/retrieval_tools.py major_profile --major "生物医学工程"
```

## R. 专业族全覆盖扩展

重点覆盖高频专业族和容易产生误解的冷热门专业。看专业画像时要区分“通用专业信息”和“某校专业信息”。

```powershell
python scripts/retrieval_tools.py major_profile --major "信息管理与信息系统"
python scripts/retrieval_tools.py major_profile --major "统计学"
python scripts/retrieval_tools.py major_profile --major "数学与应用数学"
python scripts/retrieval_tools.py major_profile --major "物理学"
python scripts/retrieval_tools.py major_profile --major "化学"
python scripts/retrieval_tools.py major_profile --major "生物科学"
python scripts/retrieval_tools.py major_profile --major "环境工程"
python scripts/retrieval_tools.py major_profile --major "食品科学与工程"
python scripts/retrieval_tools.py major_profile --major "建筑学"
python scripts/retrieval_tools.py major_profile --major "城乡规划"
python scripts/retrieval_tools.py major_profile --major "药学"
python scripts/retrieval_tools.py major_profile --major "护理学"
python scripts/retrieval_tools.py major_profile --major "新闻学"
python scripts/retrieval_tools.py major_profile --major "英语"
python scripts/retrieval_tools.py major_profile --major "金融学"
python scripts/retrieval_tools.py major_profile --major "经济学"
python scripts/retrieval_tools.py major_profile --major "财务管理"
python scripts/retrieval_tools.py major_school_list --major "网络空间安全" --province-filter "江苏" --school-level-filter "本科" --limit 30
python scripts/retrieval_tools.py major_school_list --major "信息安全" --province-filter "浙江" --school-level-filter "本科" --limit 30
python scripts/retrieval_tools.py major_school_list --major "通信工程" --province-filter "陕西" --school-level-filter "本科" --limit 30
python scripts/retrieval_tools.py major_school_list --major "机器人工程" --province-filter "广东" --school-level-filter "本科" --limit 30
python scripts/retrieval_tools.py major_school_list --major "土木工程" --province-filter "四川" --school-level-filter "本科" --limit 30
python scripts/retrieval_tools.py major_school_list --major "材料科学与工程" --province-filter "湖北" --school-level-filter "本科" --limit 30
python scripts/retrieval_tools.py major_school_list --major "药学" --province-filter "浙江" --school-level-filter "本科" --limit 30
python scripts/retrieval_tools.py major_school_list --major "护理学" --province-filter "山东" --school-level-filter "本科" --limit 30
python scripts/retrieval_tools.py major_school_list --major "新闻学" --province-filter "北京" --school-level-filter "本科" --limit 30
python scripts/retrieval_tools.py major_school_list --major "金融学" --province-filter "上海" --school-level-filter "本科" --limit 30
```

## S. 省份、科类、分数段矩阵

重点覆盖综合改革省份、3+1+2 省份、传统文理省份，以及高分、中分、低分、极端分数。

```powershell
python scripts/retrieval_tools.py score_to_rank --province "北京" --subject-type "综合" --score 640 --year 2025
python scripts/retrieval_tools.py score_to_rank --province "天津" --subject-type "综合" --score 610 --year 2025
python scripts/retrieval_tools.py score_to_rank --province "上海" --subject-type "综合" --score 560 --year 2025
python scripts/retrieval_tools.py score_to_rank --province "海南" --subject-type "综合" --score 680 --year 2025
python scripts/retrieval_tools.py score_to_rank --province "福建" --subject-type "物理" --score 590 --year 2025
python scripts/retrieval_tools.py score_to_rank --province "福建" --subject-type "历史" --score 560 --year 2025
python scripts/retrieval_tools.py score_to_rank --province "湖南" --subject-type "物理" --score 600 --year 2025
python scripts/retrieval_tools.py score_to_rank --province "湖南" --subject-type "历史" --score 570 --year 2025
python scripts/retrieval_tools.py score_to_rank --province "河北" --subject-type "物理" --score 585 --year 2025
python scripts/retrieval_tools.py score_to_rank --province "河北" --subject-type "历史" --score 555 --year 2025
python scripts/retrieval_tools.py score_to_rank --province "陕西" --subject-type "理科" --score 575 --year 2025
python scripts/retrieval_tools.py score_to_rank --province "陕西" --subject-type "文科" --score 545 --year 2025
python scripts/retrieval_tools.py score_to_rank --province "云南" --subject-type "理科" --score 540 --year 2025
python scripts/retrieval_tools.py score_to_rank --province "云南" --subject-type "文科" --score 560 --year 2025
python scripts/retrieval_tools.py score_to_rank --province "浙江" --subject-type "综合" --score 700 --year 2025
python scripts/retrieval_tools.py score_to_rank --province "浙江" --subject-type "综合" --score 280 --year 2025
python scripts/retrieval_tools.py rank_to_school_match --province "北京" --subject-type "综合" --rank 5000 --year 2025 --preferred-regions 北京 天津 上海 --limit 30
python scripts/retrieval_tools.py rank_to_school_match --province "天津" --subject-type "综合" --score 610 --year 2025 --preferred-regions 天津 北京 河北 --limit 30
python scripts/retrieval_tools.py rank_to_school_match --province "上海" --subject-type "综合" --rank 12000 --year 2025 --preferred-regions 上海 江苏 浙江 --limit 30
python scripts/retrieval_tools.py rank_to_school_match --province "福建" --subject-type "物理" --score 590 --year 2025 --preferred-regions 福建 广东 浙江 --limit 30
python scripts/retrieval_tools.py rank_to_school_match --province "湖南" --subject-type "历史" --score 570 --year 2025 --preferred-regions 湖南 湖北 广东 --limit 30
python scripts/retrieval_tools.py rank_to_school_match --province "陕西" --subject-type "理科" --rank 22000 --year 2025 --preferred-regions 陕西 四川 重庆 --limit 30
```

## T. 位次优先、分数优先与缺槽位边界

重点看工具是否优先使用位次，缺少必要槽位时是否返回 `needs_clarification`，极端分数是否稳定返回合理状态。

```powershell
python scripts/retrieval_tools.py rank_to_school_match --province "浙江" --rank 1000 --year 2025 --preferred-regions 浙江 上海 北京 --limit 20
python scripts/retrieval_tools.py rank_to_school_match --province "浙江" --rank 100000 --year 2025 --preferred-regions 浙江 江苏 安徽 --limit 20
python scripts/retrieval_tools.py rank_to_school_match --province "广东" --rank 5000 --year 2025 --preferred-regions 广东 北京 上海 --limit 20
python scripts/retrieval_tools.py rank_to_school_match --province "广东" --rank 150000 --year 2025 --preferred-regions 广东 广西 江西 --limit 20
python scripts/retrieval_tools.py rank_to_major_match --province "浙江" --major "临床医学" --rank 5000 --year 2025 --preferred-regions 浙江 上海 江苏 --limit 20
python scripts/retrieval_tools.py rank_to_major_match --province "浙江" --major "计算机" --rank 100000 --year 2025 --preferred-regions 浙江 安徽 江西 --limit 20
python scripts/retrieval_tools.py rank_to_major_match --province "广东" --major "法学" --rank 3000 --year 2025 --preferred-regions 广东 北京 上海 --limit 20
python scripts/retrieval_tools.py rank_to_major_match --province "广东" --major "护理学" --rank 120000 --year 2025 --preferred-regions 广东 广西 湖南 --limit 20
python scripts/retrieval_tools.py rank_to_school_match --province "浙江" --year 2025 --limit 10
python scripts/retrieval_tools.py rank_to_major_match --province "浙江" --major "计算机" --year 2025 --limit 10
python scripts/retrieval_tools.py rank_to_school_match --province "浙江" --subject-type "综合" --score 750 --year 2025 --limit 10
python scripts/retrieval_tools.py rank_to_school_match --province "浙江" --subject-type "综合" --score 0 --year 2025 --limit 10
python scripts/retrieval_tools.py rank_to_major_match --province "浙江" --major "计算机" --subject-type "综合" --score 750 --year 2025 --limit 10
python scripts/retrieval_tools.py rank_to_major_match --province "浙江" --major "计算机" --subject-type "综合" --score 0 --year 2025 --limit 10
```

## U. 学校-专业错配与专业大类边界

重点看工具是否能在学校不开设、招生样本缺失、大类名称不等于具体专业时给出缺口或警告。

```powershell
python scripts/retrieval_tools.py school_major_profile --school "杭州电子科技大学" --major "口腔医学" --province "浙江" --subject-type "综合" --year 2025
python scripts/retrieval_tools.py school_major_profile --school "北京邮电大学" --major "临床医学" --province "北京" --subject-type "综合" --year 2025
python scripts/retrieval_tools.py school_major_profile --school "南京航空航天大学" --major "法学" --province "江苏" --subject-type "历史" --year 2025
python scripts/retrieval_tools.py school_major_profile --school "西南交通大学" --major "口腔医学" --province "四川" --subject-type "理科" --year 2025
python scripts/retrieval_tools.py school_major_profile --school "浙江大学" --major "工科试验班" --province "浙江" --subject-type "综合" --year 2025
python scripts/retrieval_tools.py school_major_profile --school "上海交通大学" --major "电子信息类" --province "上海" --subject-type "综合" --year 2025
python scripts/retrieval_tools.py school_major_profile --school "华中科技大学" --major "临床医学类" --province "湖北" --subject-type "物理" --year 2025
python scripts/retrieval_tools.py school_major_profile --school "北京邮电大学" --major "计算机类" --province "北京" --subject-type "综合" --year 2025
python scripts/retrieval_tools.py specialty_group_lookup --school "浙江大学" --major "医学试验班" --province "浙江" --subject-type "综合" --year 2025 --limit 20
python scripts/retrieval_tools.py specialty_group_lookup --school "北京邮电大学" --major "计算机类" --province "北京" --subject-type "综合" --year 2025 --limit 20
python scripts/retrieval_tools.py specialty_group_lookup --school "上海交通大学" --major "自然科学试验班" --province "上海" --subject-type "综合" --year 2025 --limit 20
python scripts/retrieval_tools.py specialty_group_lookup --school "南京航空航天大学" --major "工科试验班" --province "江苏" --subject-type "物理" --year 2025 --limit 20
```

## V. 政策规则风险全覆盖

重点覆盖招生章程里常见高风险点：单科、语种、体检、调剂、中外合作、专项计划、师范方向、医学学制、校区。

```powershell
python scripts/retrieval_tools.py policy_rule_lookup --school "浙江大学" --policy-type "招生章程" --province "浙江" --year 2025
python scripts/retrieval_tools.py policy_rule_lookup --school "浙江大学" --policy-type "专业录取规则" --province "浙江" --year 2025
python scripts/retrieval_tools.py policy_rule_lookup --school "浙江大学" --policy-type "调剂规则" --province "浙江" --year 2025
python scripts/retrieval_tools.py policy_rule_lookup --school "上海交通大学" --policy-type "体检限制" --province "上海" --year 2025
python scripts/retrieval_tools.py policy_rule_lookup --school "华中科技大学" --policy-type "医学体检限制" --province "湖北" --year 2025
python scripts/retrieval_tools.py policy_rule_lookup --school "北京邮电大学" --policy-type "外语语种" --province "北京" --year 2025
python scripts/retrieval_tools.py policy_rule_lookup --school "西安电子科技大学" --policy-type "单科限制" --province "陕西" --year 2025
python scripts/retrieval_tools.py policy_rule_lookup --school "深圳大学" --policy-type "中外合作办学" --province "广东" --year 2025
python scripts/retrieval_tools.py policy_rule_lookup --school "南京航空航天大学" --policy-type "飞行技术身体条件" --province "江苏" --year 2025
python scripts/retrieval_tools.py policy_rule_lookup --school "华东师范大学" --policy-type "公费师范生" --province "上海" --year 2025
python scripts/retrieval_tools.py policy_rule_lookup --school "东北师范大学" --policy-type "优师专项" --province "吉林" --year 2025
python scripts/retrieval_tools.py policy_rule_lookup --school "西南大学" --policy-type "国家专项" --province "重庆" --year 2025
python scripts/retrieval_tools.py policy_rule_lookup --school "浙江大学" --policy-type "高校专项" --province "浙江" --year 2025
python scripts/retrieval_tools.py policy_rule_lookup --school "杭州电子科技大学" --policy-type "校区规则" --province "浙江" --year 2025
```

## W. 费用、校区、住宿、培养地点

重点看本地库没有稳定字段时是否返回缺口，不猜测“在哪个校区读”。

```powershell
python scripts/retrieval_tools.py fee_and_campus_lookup --school "北京邮电大学" --major "计算机类" --province "北京" --year 2025 --limit 30
python scripts/retrieval_tools.py fee_and_campus_lookup --school "西安电子科技大学" --major "电子信息类" --province "陕西" --year 2025 --limit 30
python scripts/retrieval_tools.py fee_and_campus_lookup --school "电子科技大学" --major "软件工程" --province "四川" --year 2025 --limit 30
python scripts/retrieval_tools.py fee_and_campus_lookup --school "上海交通大学" --major "自然科学试验班" --province "上海" --year 2025 --limit 30
python scripts/retrieval_tools.py fee_and_campus_lookup --school "华中科技大学" --major "临床医学" --province "湖北" --year 2025 --limit 30
python scripts/retrieval_tools.py fee_and_campus_lookup --school "华东师范大学" --major "汉语言文学" --province "上海" --year 2025 --limit 30
python scripts/retrieval_tools.py fee_and_campus_lookup --school "宁波诺丁汉大学" --major "计算机科学与技术" --province "浙江" --year 2025 --limit 30
python scripts/retrieval_tools.py fee_and_campus_lookup --school "西交利物浦大学" --major "金融学" --province "江苏" --year 2025 --limit 30
python scripts/retrieval_tools.py fee_and_campus_lookup --school "深圳北理莫斯科大学" --major "电子与计算机工程" --province "广东" --year 2025 --limit 30
python scripts/retrieval_tools.py fee_and_campus_lookup --school "香港中文大学（深圳）" --major "计算机科学与技术" --province "广东" --year 2025 --limit 30
```

## X. 招生计划和录取历史宽窄口径

重点覆盖学校全口径、专业精确口径、省份口径、年份缺省、只筛专业不筛学校等情况。

```powershell
python scripts/retrieval_tools.py plan_history --school "杭州电子科技大学" --province "浙江" --years 2025 2024 2023 --limit 100
python scripts/retrieval_tools.py plan_history --school "浙江大学" --province "浙江" --years 2025 --limit 100
python scripts/retrieval_tools.py plan_history --school "北京邮电大学" --province "北京" --years 2025 2024 --limit 100
python scripts/retrieval_tools.py plan_history --school "西安电子科技大学" --province "陕西" --years 2025 2024 --limit 100
python scripts/retrieval_tools.py plan_history --school "华东师范大学" --major "汉语言文学" --province "上海" --years 2025 2024 2023 --limit 50
python scripts/retrieval_tools.py plan_history --school "中南大学" --major "临床医学" --province "湖南" --years 2025 2024 2023 --limit 50
python scripts/retrieval_tools.py admission_history --province "浙江" --subject-type "综合" --years 2025 2024 2023 --limit 50
python scripts/retrieval_tools.py admission_history --major "计算机科学与技术" --province "浙江" --subject-type "综合" --years 2025 2024 2023 --limit 50
python scripts/retrieval_tools.py admission_history --school "杭州电子科技大学" --province "浙江" --subject-type "综合" --years 2025 2024 2023 --limit 50
python scripts/retrieval_tools.py admission_history --school "北京邮电大学" --major "计算机类" --province "北京" --subject-type "综合" --years 2025 2024 2023 --limit 50
python scripts/retrieval_tools.py admission_history --school "西安电子科技大学" --major "电子信息类" --province "陕西" --subject-type "理科" --years 2025 2024 2023 --limit 50
python scripts/retrieval_tools.py admission_history --school "华东师范大学" --major "汉语言文学" --province "上海" --subject-type "综合" --years 2025 2024 2023 --limit 50
```

## Y. 就业、升学、市场与考公交叉验证

重点防止把第三方市场样本当学校就业质量报告，把考公文本命中当正式可报。

```powershell
python scripts/retrieval_tools.py employment_summary --school "北京邮电大学" --limit 5
python scripts/retrieval_tools.py employment_summary --school "西安电子科技大学" --limit 5
python scripts/retrieval_tools.py employment_summary --school "电子科技大学" --limit 5
python scripts/retrieval_tools.py employment_summary --school "华东师范大学" --limit 5
python scripts/retrieval_tools.py employment_summary --school "中南大学" --limit 5
python scripts/retrieval_tools.py major_market_reference --major "通信工程" --sample-limit 20
python scripts/retrieval_tools.py major_market_reference --major "网络空间安全" --sample-limit 20
python scripts/retrieval_tools.py major_market_reference --major "信息安全" --sample-limit 20
python scripts/retrieval_tools.py major_market_reference --major "金融学" --sample-limit 20
python scripts/retrieval_tools.py major_market_reference --major "新闻学" --sample-limit 20
python scripts/retrieval_tools.py major_market_reference --major "护理学" --sample-limit 20
python scripts/retrieval_tools.py major_market_reference --major "土木工程" --sample-limit 20
python scripts/retrieval_tools.py civil_service_mapping --major "新闻学" --year 2026 --limit 20
python scripts/retrieval_tools.py civil_service_mapping --major "经济学" --year 2026 --limit 20
python scripts/retrieval_tools.py civil_service_mapping --major "金融学" --year 2026 --limit 20
python scripts/retrieval_tools.py civil_service_mapping --major "统计学" --year 2026 --limit 20
python scripts/retrieval_tools.py civil_service_mapping --major "药学" --year 2026 --limit 20
python scripts/retrieval_tools.py civil_service_role_search --major "新闻学" --province "北京" --year 2026 --limit 20
python scripts/retrieval_tools.py civil_service_role_search --major "经济学" --province "浙江" --year 2026 --limit 20
python scripts/retrieval_tools.py civil_service_role_search --major "金融学" --province "上海" --year 2026 --limit 20
python scripts/retrieval_tools.py civil_service_role_search --major "统计学" --province "广东" --year 2026 --limit 20
python scripts/retrieval_tools.py civil_service_role_search --major "药学" --province "四川" --year 2026 --limit 20
```

## Z. 结构化对比扩展

重点覆盖学校对比、专业对比、学校-专业方案对比，以及用户偏好上下文输入。

```powershell
python scripts/retrieval_tools.py comparison_query --target-type school --target "北京邮电大学" --target "西安电子科技大学" --dimension school_profile --dimension admission --dimension employment --limit 10
python scripts/retrieval_tools.py comparison_query --target-type school --target "电子科技大学" --target "西安电子科技大学" --dimension school_profile --dimension admission --dimension employment --limit 10
python scripts/retrieval_tools.py comparison_query --target-type school --target "华东师范大学" --target "南京师范大学" --dimension school_profile --dimension admission --dimension employment --limit 10
python scripts/retrieval_tools.py comparison_query --target-type school --target "中南大学" --target "华中科技大学" --dimension school_profile --dimension admission --dimension employment --limit 10
python scripts/retrieval_tools.py comparison_query --target-type major --target "通信工程" --target "电子信息工程" --dimension major_profile --dimension market_reference --dimension civil_service --limit 10
python scripts/retrieval_tools.py comparison_query --target-type major --target "网络空间安全" --target "信息安全" --dimension major_profile --dimension market_reference --dimension civil_service --limit 10
python scripts/retrieval_tools.py comparison_query --target-type major --target "金融学" --target "会计学" --dimension major_profile --dimension market_reference --dimension civil_service --limit 10
python scripts/retrieval_tools.py comparison_query --target-type major --target "临床医学" --target "口腔医学" --dimension major_profile --dimension market_reference --dimension policy --limit 10
python scripts/retrieval_tools.py comparison_query --target-type school_major --target "北京邮电大学" --target "西安电子科技大学" --major "计算机类" --province "北京" --subject-type "综合" --score 640 --year 2025 --dimension school_major_profile --dimension admission --dimension market_reference --limit 10
python scripts/retrieval_tools.py comparison_query --target-type school_major --target "电子科技大学" --target "重庆邮电大学" --major "通信工程" --province "四川" --subject-type "理科" --rank 18000 --year 2025 --dimension school_major_profile --dimension admission --dimension market_reference --limit 10
python scripts/retrieval_tools.py comparison_query --target-type school_major --target "华东师范大学" --target "南京师范大学" --major "汉语言文学" --province "上海" --subject-type "综合" --rank 9000 --year 2025 --dimension school_major_profile --dimension admission --dimension employment --limit 10
python scripts/retrieval_tools.py comparison_query --target-type school_major --target "中南大学" --target "华中科技大学" --major "临床医学" --province "湖南" --subject-type "物理" --score 630 --year 2025 --dimension school_major_profile --dimension admission --dimension policy --limit 10
```

## AA. 数据缺口精细化检测

重点覆盖 `data_gap_detection` 支持的全部问题类型，以及字段从空、部分具备、几乎齐全到未知问题类型的状态。

```powershell
python scripts/retrieval_tools.py data_gap_detection --question-type school_major_profile --available-fields school_basic
python scripts/retrieval_tools.py data_gap_detection --question-type school_major_profile --available-fields school_basic major_basic school_major subject_eval school_major_salary school_major_regions top_companies civil_service_mapping transfer_policy streaming_ratio official_major_intro
python scripts/retrieval_tools.py data_gap_detection --question-type major_market_reference
python scripts/retrieval_tools.py data_gap_detection --question-type major_market_reference --available-fields market_snapshot
python scripts/retrieval_tools.py data_gap_detection --question-type major_market_reference --available-fields market_snapshot job_samples official_employment
python scripts/retrieval_tools.py data_gap_detection --question-type civil_service_role_search
python scripts/retrieval_tools.py data_gap_detection --question-type civil_service_role_search --available-fields role_candidates
python scripts/retrieval_tools.py data_gap_detection --question-type civil_service_role_search --available-fields role_candidates official_role_table manual_mapping
python scripts/retrieval_tools.py data_gap_detection --question-type comparison_query
python scripts/retrieval_tools.py data_gap_detection --question-type comparison_query --available-fields target_profiles admission_context
python scripts/retrieval_tools.py data_gap_detection --question-type comparison_query --available-fields target_profiles admission_context employment_context decision_preferences
python scripts/retrieval_tools.py data_gap_detection --question-type major_streaming_policy_lookup
python scripts/retrieval_tools.py data_gap_detection --question-type major_streaming_policy_lookup --available-fields official_streaming_policy
python scripts/retrieval_tools.py data_gap_detection --question-type major_streaming_policy_lookup --available-fields official_streaming_policy streaming_ratio unpopular_major_ratio
python scripts/retrieval_tools.py data_gap_detection --question-type civil_service_mapping
python scripts/retrieval_tools.py data_gap_detection --question-type civil_service_mapping --available-fields official_role_table
python scripts/retrieval_tools.py data_gap_detection --question-type civil_service_mapping --available-fields official_role_table eligibility_rules manual_major_mapping
python scripts/retrieval_tools.py data_gap_detection --question-type policy_rule_lookup
python scripts/retrieval_tools.py data_gap_detection --question-type policy_rule_lookup --available-fields official_admission_rule
python scripts/retrieval_tools.py data_gap_detection --question-type policy_rule_lookup --available-fields official_admission_rule single_subject_limit physical_exam_limit language_limit
```

## AB. 高频志愿问题组合套件补充

这些套件按用户真实问法组织，适合做端到端人工检查。

### AB1. “我高分，学校优先，想冲 985，但不想被冷门专业困住”

```powershell
python scripts/retrieval_tools.py score_to_rank --province "浙江" --subject-type "综合" --score 670 --year 2025
python scripts/retrieval_tools.py rank_to_school_match --province "浙江" --subject-type "综合" --score 670 --year 2025 --reference-years 2024 2023 --preferred-regions 浙江 上海 北京 江苏 --school-level-filter "985" --limit 30
python scripts/retrieval_tools.py rank_to_major_match --province "浙江" --major "工科试验班" --subject-type "综合" --score 670 --year 2025 --preferred-regions 浙江 上海 北京 江苏 --limit 30
python scripts/retrieval_tools.py specialty_group_risk --school "浙江大学" --province "浙江" --subject-type "综合" --year 2025 --major "工科试验班"
python scripts/retrieval_tools.py policy_rule_lookup --school "浙江大学" --policy-type "调剂规则" --province "浙江" --year 2025
python scripts/retrieval_tools.py data_gap_detection --question-type major_streaming_policy_lookup --available-fields school_basic major_basic plan_history
```

### AB2. “中分段，专业优先，想读电气或自动化”

```powershell
python scripts/retrieval_tools.py score_to_rank --province "山东" --subject-type "综合" --score 585 --year 2025
python scripts/retrieval_tools.py rank_to_major_match --province "山东" --major "电气工程及其自动化" --subject-type "综合" --score 585 --year 2025 --preferred-regions 山东 江苏 河北 天津 --limit 30
python scripts/retrieval_tools.py rank_to_major_match --province "山东" --major "自动化" --subject-type "综合" --score 585 --year 2025 --preferred-regions 山东 江苏 河北 天津 --limit 30
python scripts/retrieval_tools.py major_profile --major "电气工程及其自动化"
python scripts/retrieval_tools.py major_profile --major "自动化"
python scripts/retrieval_tools.py comparison_query --target-type major --target "电气工程及其自动化" --target "自动化" --dimension major_profile --dimension market_reference --dimension civil_service --limit 10
```

### AB3. “历史类，想学法学或汉语言，将来考公”

```powershell
python scripts/retrieval_tools.py score_to_rank --province "广东" --subject-type "历史" --score 580 --year 2025
python scripts/retrieval_tools.py rank_to_major_match --province "广东" --major "法学" --subject-type "历史" --score 580 --year 2025 --preferred-regions 广东 北京 上海 湖北 --limit 30
python scripts/retrieval_tools.py rank_to_major_match --province "广东" --major "汉语言文学" --subject-type "历史" --score 580 --year 2025 --preferred-regions 广东 北京 上海 湖北 --limit 30
python scripts/retrieval_tools.py civil_service_mapping --major "法学" --province "广东" --year 2026 --limit 20
python scripts/retrieval_tools.py civil_service_mapping --major "汉语言文学" --province "广东" --year 2026 --limit 20
python scripts/retrieval_tools.py comparison_query --target-type major --target "法学" --target "汉语言文学" --dimension major_profile --dimension civil_service --dimension market_reference --limit 10
```

### AB4. “想学医，必须检查哪些风险？”

```powershell
python scripts/retrieval_tools.py major_lookup --major "临床"
python scripts/retrieval_tools.py major_lookup --major "口腔"
python scripts/retrieval_tools.py major_profile --major "临床医学"
python scripts/retrieval_tools.py major_profile --major "口腔医学"
python scripts/retrieval_tools.py rank_to_major_match --province "江苏" --major "临床医学" --subject-type "物理" --score 635 --year 2025 --preferred-regions 江苏 浙江 上海 湖北 --limit 30
python scripts/retrieval_tools.py subject_requirement_lookup --major "临床医学" --province "江苏" --subject-type "物理" --year 2025 --limit 30
python scripts/retrieval_tools.py policy_rule_lookup --school "华中科技大学" --policy-type "医学体检限制" --province "湖北" --year 2025
python scripts/retrieval_tools.py comparison_query --target-type major --target "临床医学" --target "口腔医学" --dimension major_profile --dimension admission --dimension policy --limit 10
```

### AB5. “预算敏感，不想读高学费或不清楚校区的项目”

```powershell
python scripts/retrieval_tools.py fee_and_campus_lookup --school "宁波诺丁汉大学" --major "计算机科学与技术" --province "浙江" --year 2025 --limit 30
python scripts/retrieval_tools.py fee_and_campus_lookup --school "西交利物浦大学" --major "金融学" --province "江苏" --year 2025 --limit 30
python scripts/retrieval_tools.py fee_and_campus_lookup --school "杭州电子科技大学" --major "计算机科学与技术" --province "浙江" --year 2025 --limit 30
python scripts/retrieval_tools.py policy_rule_lookup --school "宁波诺丁汉大学" --policy-type "中外合作办学" --province "浙江" --year 2025
python scripts/retrieval_tools.py policy_rule_lookup --school "西交利物浦大学" --policy-type "中外合作办学" --province "江苏" --year 2025
python scripts/retrieval_tools.py data_gap_detection --question-type policy_rule_lookup --available-fields official_admission_rule
```

### AB6. “省内优先，能不能不出省？”

```powershell
python scripts/retrieval_tools.py score_to_rank --province "浙江" --subject-type "综合" --score 590 --year 2025
python scripts/retrieval_tools.py rank_to_school_match --province "浙江" --subject-type "综合" --score 590 --year 2025 --preferred-regions 浙江 --limit 50
python scripts/retrieval_tools.py rank_to_major_match --province "浙江" --major "计算机" --subject-type "综合" --score 590 --year 2025 --preferred-regions 浙江 --limit 50
python scripts/retrieval_tools.py rank_to_major_match --province "浙江" --major "电气" --subject-type "综合" --score 590 --year 2025 --preferred-regions 浙江 --limit 50
python scripts/retrieval_tools.py comparison_query --target-type school --target "杭州电子科技大学" --target "浙江工业大学" --dimension school_profile --dimension admission --dimension employment --limit 10
```

### AB7. “城市优先，只考虑长三角”

```powershell
python scripts/retrieval_tools.py rank_to_school_match --province "安徽" --subject-type "理科" --score 585 --year 2025 --preferred-regions 上海 江苏 浙江 安徽 --limit 50
python scripts/retrieval_tools.py rank_to_major_match --province "安徽" --major "计算机" --subject-type "理科" --score 585 --year 2025 --preferred-regions 上海 江苏 浙江 安徽 --limit 50
python scripts/retrieval_tools.py rank_to_major_match --province "安徽" --major "电子信息" --subject-type "理科" --score 585 --year 2025 --preferred-regions 上海 江苏 浙江 安徽 --limit 50
python scripts/retrieval_tools.py comparison_query --target-type school_major --target "南京邮电大学" --target "杭州电子科技大学" --major "通信工程" --province "安徽" --subject-type "理科" --score 585 --year 2025 --dimension school_major_profile --dimension admission --dimension market_reference --limit 10
```

### AB8. “保本科优先，专业可以宽一点”

```powershell
python scripts/retrieval_tools.py score_to_rank --province "河南" --subject-type "理科" --score 465 --year 2025
python scripts/retrieval_tools.py rank_to_school_match --province "河南" --subject-type "理科" --score 465 --year 2025 --school-level-filter "本科" --preferred-regions 河南 河北 山西 安徽 --limit 50
python scripts/retrieval_tools.py rank_to_major_match --province "河南" --major "计算机" --subject-type "理科" --score 465 --year 2025 --school-level-filter "本科" --preferred-regions 河南 河北 山西 安徽 --limit 50
python scripts/retrieval_tools.py rank_to_major_match --province "河南" --major "会计学" --subject-type "理科" --score 465 --year 2025 --school-level-filter "本科" --preferred-regions 河南 河北 山西 安徽 --limit 50
python scripts/retrieval_tools.py data_gap_detection --question-type comparison_query --available-fields target_profiles admission_context decision_preferences
```

### AB9. “我不想去冷门专业，专业组里要逐项看”

```powershell
python scripts/retrieval_tools.py specialty_group_lookup --school "浙江大学" --province "浙江" --subject-type "综合" --year 2025 --limit 30
python scripts/retrieval_tools.py specialty_group_lookup --school "浙江大学" --major "工科试验班" --province "浙江" --subject-type "综合" --year 2025 --limit 30
python scripts/retrieval_tools.py specialty_group_risk --school "浙江大学" --province "浙江" --subject-type "综合" --year 2025 --major "计算机科学与技术"
python scripts/retrieval_tools.py major_streaming_policy_lookup --school "浙江大学" --major "工科试验班" --province "浙江" --year 2025 --limit 20
python scripts/retrieval_tools.py data_gap_detection --question-type major_streaming_policy_lookup --available-fields official_streaming_policy
```

### AB10. “学校就业好，是不是代表这个专业就业好？”

```powershell
python scripts/retrieval_tools.py employment_summary --school "杭州电子科技大学" --limit 5
python scripts/retrieval_tools.py school_major_profile --school "杭州电子科技大学" --major "计算机科学与技术" --province "浙江" --subject-type "综合" --year 2025
python scripts/retrieval_tools.py major_market_reference --major "计算机科学与技术" --sample-limit 20
python scripts/retrieval_tools.py data_gap_detection --question-type school_major_profile --available-fields school_basic major_basic school_major subject_eval
python scripts/retrieval_tools.py source_trace_lookup --tool-name employment_summary
python scripts/retrieval_tools.py source_trace_lookup --tool-name major_market_reference
```

## AC. 最终人工验收清单

跑完任意一组命令后，按以下清单看结构和口径：

- `status` 是否符合输入条件：完整命中应为 `ok` 或 `partial`，缺槽位应为 `needs_clarification`，无样本应为 `not_found`。
- `normalized_slots` 是否正确处理学校简称、专业简称、省份、年份、科类、分数和位次。
- `source_tables` 是否能解释结果来自哪类本地表。
- `scope_notes` 是否明确区分学校级、专业通用级、校专业级、专业组级、招生计划、录取历史和市场样本。
- `warnings` 是否提示历史录取不保证未来、专业组不等于真实分流、岗位命中不等于正式可报、第三方市场样本不等于官方就业。
- `data_gaps` 是否把缺失项说清楚，尤其是官方章程、校专业薪资、校专业去向、校区、真实分流比例、正式考公资格判定。
- 对比类结果是否只给并列证据，不直接替用户作最终选择。
- 极端输入、模糊输入和错配输入是否稳定返回边界状态，而不是猜测。
