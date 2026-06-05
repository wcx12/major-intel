# 来源引用与署名说明

本目录下的数据集使用了第三方开源仓库中的公开材料。请在后续分发、展示、论文、报告或产品文档中保留本文件，并按各源仓库许可证要求进行署名。

## 直接对话数据来源

| 来源 | GitHub | 许可证 | 本数据集中的使用方式 |
| --- | --- | --- | --- |
| `Xue-Feng-Skill` | https://github.com/SPA3K/Xue-Feng-Skill | MIT | `llm_cleaned_dialogues.jsonl`、`question_bank.jsonl`、`function_call_eval_cases.jsonl` 中 152 条对话清洗记录均衍生自该仓库 `data/transcripts/` 下的公开视频 ASR 转写。 |

说明：

- 每条清洗记录均保留 `source_repo`、`source_ref`、`response_candidate_ref` 字段，可追溯到本地源文件和 segment。
- `Xue-Feng-Skill` README 说明其 `data/transcripts/` 包含 137 个视频的 OpenAI Whisper `base` ASR 转写；ASR 可能存在专有名词、断句、说话人边界错误。
- 本项目对 ASR 做了结构化清洗、字段抽取和质量标注，但未把清洗结果声明为原作者原文或官方招生事实。

建议引用格式：

```text
对话候选语料衍生自 SPA3K/Xue-Feng-Skill 项目的公开视频 ASR 转写：
https://github.com/SPA3K/Xue-Feng-Skill
本项目在其基础上进行了问题抽取、双版本清洗、策略摘要和 function-call eval 标注。
```

## 策略与风格参考来源

以下来源没有作为 152 条对话记录的 `source_repo` 主来源，但用于导师策略库、风格参考、问题族设计或人工整理判断。

| 来源 | GitHub | 许可证 | 本数据集中的使用方式 |
| --- | --- | --- | --- |
| `zhangxuefeng-skillset` | https://github.com/Eric-Yibo-Shen/zhangxuefeng-skillset | knowledge/prompts 为 CC BY 4.0；代码许可证见源仓库 | 用于 `mentor_strategy_bank.jsonl` 中部分策略框架参考，例如志愿填报、专业选择、院校选择方法论。 |
| `gaokao-mentor-wisdom` | https://github.com/dongsheng123132/gaokao-mentor-wisdom | MIT | 用于策略整理参考；该项目内容多为公开语录整理或转述，不应当作逐字原始对话。 |
| `zhangxuefeng-skill` | https://github.com/alchaincyf/zhangxuefeng-skill | MIT | 用于风格和策略参考；不作为事实数据源。 |
| `zhang-xuefeng-memorial` | https://github.com/bcefghj/zhang-xuefeng-memorial | CC BY 4.0 | 仅作为观点整理类参考，不进入事实主链路或真实对话主链路。 |

## 本项目内部来源

| 来源 | 用途 |
| --- | --- |
| `docs/specs/data-gap-queue.md` | `mentor_strategy_bank.jsonl` 中数据缺口、转专业政策查询等策略的本项目内部规范参考。 |
| `scripts/build_dialogue_assets.py` | 负责从源材料抽取候选、调用 Claude Code 清洗、校验字段并生成本目录产物。 |

## 署名与使用边界

- 请不要把 `mentor_strategy` 或策略库内容当作第三方仓库作者的逐字原话。
- 请不要把 ASR 清洗结果当作官方招生数据、录取承诺或院校事实标准答案。
- 如果继续分发本目录数据，建议同时保留：
  - `README.md`
  - `SOURCES.md`
  - `source_inventory.json`
  - 各记录中的 `source_repo` / `source_ref` 字段
- 如果产品中展示具体院校、专业、分数、位次、录取概率、转专业政策等事实判断，必须另接官方招生章程、考试院、学校官网或本项目事实检索工具二次核验。
