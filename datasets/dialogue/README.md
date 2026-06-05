# 高考志愿对话数据集目录

本目录保存可以提交到 Git 的对话数据集快照和清单。它和本地生成目录的边界如下：

- `datasets/dialogue/`：经过筛选、可复现、可作为评测基线的小型公开快照。
- `data/processed/dialogue/`：本地重新生成的产物，默认被 `.gitignore` 排除。
- `clean/`：历史清洗或本地实验目录，后续逐步迁移或归档，不再作为正式入口。

## 当前快照

- `claude_full/`：已提交的 Claude 清洗全量快照，包含问题库、function-call 评测用例、导师策略摘要、来源清单和质量报告。

## 构建入口

推荐命令：

```powershell
python scripts/datasets/build_dialogue_assets.py --limit 10 --output-dir data/processed/dialogue_smoke
```

兼容旧命令：

```powershell
python scripts/build_dialogue_assets.py --limit 10 --output-dir data/processed/dialogue_smoke
```

真实实现位于 `src/major_intel/datasets/dialogue/build_dialogue_assets.py`。脚本默认输出到 `data/processed/dialogue/`，避免误覆盖已提交快照。

## 使用边界

这些数据来自公开 ASR 和资料片段的清洗结果，适合用于问题意图覆盖、function-call 选择评测和回答策略参考。涉及院校、专业、录取、就业等事实判断时，仍必须调用本项目的检索工具或官方证据链二次核验。
