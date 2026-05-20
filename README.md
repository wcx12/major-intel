# Major Intel

面向高考志愿、院校专业选择与数据可信问答的本地情报系统。

这个仓库的目标不是做一个只会聊天的专业介绍机器人，而是把学校、专业、录取位次、就业市场、考公岗位、转专业政策等信息整理成可追溯、可测试、可复核的检索能力。系统回答时必须区分事实、推断和建议，并在数据不足时明确返回缺口。

## 当前状态

截至 2026-05-20，仓库已经具备以下主干能力：

- 本地检索 MVP：学校、专业、学校专业组合、历年录取、分数位次转换、学校层面冲稳保匹配。
- Function call 工具层：13 个检索入口已接入 schema、dispatcher、单元测试和 smoke runner。
- rysxai 市场数据链路：专业市场样本 crawler、报告渲染、就业市场概览与 dashboard 构建脚本。
- rysxai 考公数据链路：2026 公考岗位 crawler、CSV 展平与样本检索入口。
- rysxai 转专业政策链路：学校列表 seed、转专业政策 crawler、静态 dashboard 构建脚本。
- 数据安全边界：原始抓取、处理结果、日志、SQL dump 和本地外部资料默认不提交。

更细的完成清单见 [当前状态快照](docs/status/current-state.md)。

## 目录索引

```text
docs/research/                  起点调研与背景材料
docs/specs/                     数据模型、检索工具、采集与接入方案
docs/status/                    当前实现状态与阶段性整理
scripts/local_retrieval_mvp.py  本地检索 CLI MVP
scripts/retrieval_tools.py      标准检索工具层
scripts/retrieval_function_registry.py
                                 function schema 注册与 dispatcher
scripts/run_retrieval_smoke_cases.py
                                 本地 smoke case runner
scripts/rysxai_*                rysxai 数据采集、报告和 dashboard 工具
data/seeds/                     可提交的小型种子数据
tests/                          单元测试
```

## 常用命令

运行单元测试：

```bash
python -m unittest discover -s tests
```

运行本地检索 MVP 示例：

```bash
python scripts/local_retrieval_mvp.py \
  --school "杭州电子科技大学" \
  --major "机械设计制造及其自动化"
```

运行 retrieval smoke cases：

```bash
python scripts/run_retrieval_smoke_cases.py --cases data/retrieval_smoke_cases.json
```

刷新 rysxai 学校 seed：

```bash
python scripts/rysxai_transfer_policy_crawler.py --refresh-university-list --list-only
```

构建转专业政策 dashboard：

```bash
python scripts/build_rysxai_transfer_policy_dashboard.py
```

## 数据边界

- `data/raw/`、`data/processed/`、`data/logs/` 是本地运行产物，默认不提交。
- `reports/rysxai/` 和 retrieval smoke JSON 是生成结果，默认不提交。
- `gaokao_test_*.sql` 和 `*.db` 是本地数据库产物，默认不提交。
- `gaokao-zhiyuan-projects/` 是外部参考项目集合，默认不纳入本仓库版本历史。

## 回答原则

1. 所有结论都要能追溯到来源、表、字段或明确的数据缺口。
2. 学校级、专业通用级、校专业级、招生专业组级数据不能混用。
3. rysxai 等第三方市场样本只能作为市场观察，不代表官方校专业就业结论。
4. 历史录取分和位次只代表历史样本，不保证未来录取。
5. 数据缺失时进入缺口队列或人工复核路径，不编造答案。
