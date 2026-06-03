# transfer_policy_lookup

## 1. 工具原理

`transfer_policy_lookup` 查询学校转专业政策线索。它先解析学校，再读取已采集的转专业政策数据或缺口信息。

## 2. 输入与输出

- 主要输入：`school_text`。
- 可选输入：年份、关键词。
- 关键输出：政策文本线索、来源链接、限制条件、缺口提示。

## 3. 状态语义

- `ok`：命中转专业政策线索。
- `not_found`：没有政策记录。
- `needs_clarification`：学校输入缺失或歧义。
- `partial`：只命中线索但不足以做正式规则判断。

## 4. 测试范围

当前仅完成目录和 README 结构。后续应覆盖学校解析传播、政策命中、政策缺失、年份过滤、来源缺失。

## 5. 测试结果

- 最近运行日期：尚未运行专属测试。
- 运行命令：待补充。
- 运行结果：待补充。

## 6. 已知风险与待改善

- 转专业政策需要官方来源复核。
- 需要补充“不能直接承诺可转”的 warnings 测试。

## 7. 关联文件

- 实现：[scripts/retrieval_tools.py](../../../scripts/retrieval_tools.py)
- 相关爬虫：[scripts/rysxai_transfer_policy_crawler.py](../../../scripts/rysxai_transfer_policy_crawler.py)
