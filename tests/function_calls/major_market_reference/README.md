# major_market_reference

## 1. 工具原理

`major_market_reference` 查询专业对应的市场参考信息，包括岗位样本、薪资或行业分布等非录取类数据。它先解析专业，再查市场快照和岗位样本。

## 2. 输入与输出

- 主要输入：`major_text`，可选 `sample_limit`。
- 关键输出：市场快照、岗位样本、行业或薪资线索。
- 重要说明：市场样本不代表某学校该专业就业质量。

## 3. 状态语义

- `ok`：命中市场快照或岗位样本。
- `not_found`：专业未命中或没有市场样本。
- `needs_clarification`：专业输入缺失。
- `partial`：只有部分市场线索。

## 4. 测试范围

当前仅完成目录和 README 结构。后续应覆盖专业解析、样本限制、无快照、无岗位、市场数据口径 warnings。

## 5. 测试结果

- 最近运行日期：尚未运行专属测试。
- 运行命令：待补充。
- 运行结果：待补充。

## 6. 已知风险与待改善

- 市场数据是参考样本，不能代表稳定就业结论。
- 需要补充样本不足和薪资字段缺失测试。

## 7. 关联文件

- 实现：[scripts/retrieval_tools.py](../../../scripts/retrieval_tools.py)
- 相关爬虫：[scripts/rysxai_market_crawler.py](../../../scripts/rysxai_market_crawler.py)
