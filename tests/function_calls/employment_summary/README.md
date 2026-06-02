# employment_summary

## 1. 工具原理

`employment_summary` 查询学校层面的就业和升学摘要。它先解析学校，再读取学校就业相关表中的最新若干条摘要。

## 2. 输入与输出

- 主要输入：`school_text`，可选 `limit`。
- 关键输出：`records`，每条包含就业率、升学率、平均薪资、`employment_data`、行业/地域/雇主等学校层面字段。
- 重要说明：学校层面就业数据不能代表某个专业的就业情况。

## 3. 状态语义

- `ok`：命中就业摘要。
- `not_found`：没有就业摘要记录。
- `needs_clarification`：学校输入缺失或歧义。
- `partial`：有就业摘要记录，但只有年份或核心字段为空；工具会在 `data_gaps` 标出“学校级就业/升学摘要有效字段”。

## 4. 测试范围

已覆盖学校解析传播、空结果、学校层面口径 warnings，以及只有年份/空字段时返回 `partial`。

## 5. 测试结果

- 最近运行日期：2026-06-02。
- 运行命令：`python -m unittest tests.test_retrieval_tools`
- 运行结果：通过。

## 6. 已知风险与待改善

- 数据可能来自学校报告，年份和统计口径差异较大。
- 即使 `records` 可用，也只能支持学校层面摘要；不能代表某专业就业。

## 7. 关联文件

- 实现：[scripts/retrieval_tools.py](../../../scripts/retrieval_tools.py)
