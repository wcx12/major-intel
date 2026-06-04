# 高考志愿对话数据清洗策略记录

日期：2026-05-23

本文记录本轮从高考志愿相关 GitHub 仓库中清洗“考生/家长常问问题”和“导师回复策略”的口径，便于后续复跑、人工复核和继续用 Claude Code 做分批精洗。

## 1. 原始数据口径

### 真实对话来源

只把 `Xue-Feng-Skill/data/transcripts/*.json` 作为真实对话来源。

- 原始 ASR JSON 转录文件：137 个
- 清洗脚本从中抽出的候选问答片段：152 条
- 清洗后全量问题库：152 条
- 建议优先直接使用的问题库：126 条
- 需要复核的问题：114 条

这些数据来自公开视频 ASR，文本有口语、省略、识别错误和话题跳转，因此只能作为“真实问法/回答策略候选”，不能直接当作事实标准答案。

### 策略参考来源

策略来源不等于真实对话数据，主要用于抽取回答方法论。

- `gaokao-mentor-wisdom/exports/rag_chunks.jsonl`：105 条观点/策略 chunk
- `zhangxuefeng-skillset/knowledge/*.md`：14 个方法论 markdown 文档
- `zhangxuefeng-skill`、`zhang-xuefeng-memorial` 等仓库：作为风格、提示词或方法论参考

### 不进入真实对话集的数据

以下内容不能混入真实对话数据集：

- demo conversation
- prompt 示例
- synthetic fine-tune 样例
- 纪念/观点整理类非原始对话文本

这些内容只能用于“策略参考”或“风格参考”。

## 2. 清洗目标

本轮清洗不是为了生成最终标准答案，而是产出两类后续可用资产：

1. 考生/家长常问问题  
   用于测试模型检索能力和 function-call 覆盖能力。

2. 导师回复策略  
   用于约束模型回答路径，例如先查什么、什么时候追问、哪些结论不能说满。

## 3. 字段设计

每条问题保留三层文本：

- `question_raw`：原始 ASR 问题片段，不改写，用于追溯。
- `question_colloquial_clean`：轻清洗口语版，保留真实问法风格。
- `question_normalized`：标准化测试问法，用于检索和 function-call 测试。

回答部分保留两层：

- `response_candidate_raw`：问题后最多 6 个 ASR segment 的候选回答原文。
- `mentor_strategy`：从回答片段或方法论中抽取出的策略摘要，不当作导师原话。

## 4. 规则清洗流程

脚本入口：

```bash
python scripts/build_dialogue_assets.py --cleaner rules
```

核心流程：

1. 读取 `Xue-Feng-Skill/data/transcripts/*.json`。
2. 逐个 ASR segment 判断是否像考生/家长问题。
3. 命中问题后，向后取最多 6 个 segment 作为候选回答。
4. 对问题做轻清洗，保留口语风格。
5. 抽取槽位：省份、科类、分数、位次、学校、专业、城市偏好、职业偏好等。
6. 归类问题类型，例如：
   - `rank_to_school_match`
   - `rank_to_major_match`
   - `major_profile`
   - `employment_summary`
   - `school_major_profile`
   - `specialty_group_risk`
   - `transfer_policy_lookup`
7. 根据问题类型映射 expected tools。
8. 从候选回答中抽取导师策略。
9. 按质量分层，输出全量集、可用集和复核队列。

## 5. 问题筛选规则

ASR segment 需要同时满足：

- 长度不过短，也不过长。
- 包含高考志愿相关关键词，例如专业、学校、分数、位次、就业、前景、考研、公务员等。
- 包含问题线索，例如“问”“能不能”“报什么”“推荐”“怎么样”“吗”等。
- 匹配常见问法模式。

这一步会保留真实口语噪声，但会尽量过滤明显不是提问的讲述片段。

## 6. 质量分层

输出分两套：

- 全量集：保留所有候选，用于鲁棒性测试和人工继续清洗。
- 可用集：只保留 A/B 级问题，建议先用于模型检索和 function-call 测试。

当前产物：

- `clean/dialogue/question_bank.jsonl`：152 条
- `clean/dialogue/usable_question_bank.jsonl`：126 条
- `clean/dialogue/function_call_eval_cases.jsonl`：152 条
- `clean/dialogue/usable_function_call_eval_cases.jsonl`：126 条
- `clean/dialogue/review_queue.jsonl`：114 条

需要复核的典型原因：

- ASR 识别错误较多。
- 省份、科类、分数或位次缺失。
- 问题和回答边界不清。
- 片段更像导师讲述，不像学生/家长提问。

## 7. 导师策略抽取口径

策略不是标准答案，而是回答路径。当前抽取了 5 条通用策略模板：

1. 位次优先，再按专业偏好做冲稳保。
2. 专业判断先看就业面、学校层次和家庭承受力。
3. 学校专业组合要区分学校级、专业级和专业组级口径。
4. 专业组风险只能初筛，不能编造真实调剂比例。
5. 转专业必须查官方政策，没有来源就标缺口。

另外，从 ASR 回答片段中归纳高频策略，例如：

- 缺省份、科类、分数时先追问关键信息。
- 色弱/体检受限先查受限专业。
- 先看位次，再看近年录取位次。
- 本科录取和考研/升学分两步规划。
- 就业建议要落到岗位、行业和长期发展，不只看专业名称。

## 8. Claude Code 精洗策略

本地 Claude Code 已验证可用，但不适合同步全量清洗。

已跑样本：

- `clean/dialogue_claude_sample/llm_cleaned_dialogues.jsonl`：3 条
- 其中可直接使用：1 条

建议后续使用方式：

1. 先用规则版产出全量集。
2. 从 `review_queue.jsonl` 或高价值问题类型中抽样。
3. 分小批调用 Claude Code。
4. Claude 只做结构化标注和轻清洗，不新增事实。
5. Claude 输出必须再经过本地 schema 校验和人工抽检。

不建议一次性全量调用 Claude，因为当前启动和生成耗时较高，且部分 ASR 噪声片段即使用大模型也只能判废。

## 9. 后续推荐用法

优先使用：

- `usable_question_bank.jsonl` 做真实问法检索测试。
- `usable_function_call_eval_cases.jsonl` 做 function-call 覆盖测试。
- `mentor_strategy_bank.jsonl` 约束回答路径。
- `mentor_reply_strategies.md` 给人工阅读策略。

压力测试使用：

- `question_bank.jsonl`
- `function_call_eval_cases.jsonl`

人工继续清洗使用：

- `review_queue.jsonl`
- `asr_question_candidates.jsonl`
- `dialogue_claude_sample/llm_cleaned_dialogues.jsonl`

## 10. 复跑命令

规则版全量清洗：

```bash
python scripts/build_dialogue_assets.py --cleaner rules
```

Claude 小样本精洗：

```bash
python scripts/build_dialogue_assets.py --cleaner claude --limit 3 --claude-batch-size 3 --claude-timeout-seconds 90 --output-dir clean/dialogue_claude_sample
```

验证：

```bash
python -m pytest tests/test_build_dialogue_assets.py -q
```
