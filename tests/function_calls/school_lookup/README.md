# school_lookup

## 1. 工具原理

`school_lookup` 用来把用户输入的学校名称、简称、外号、学校代码或内部 `school_id` 解析为本地标准学校实体。当前逻辑会先查 `entity_aliases` 中已确认的学校别名候选，再按需回退查询 `edu_university`。

核心流程：

- 如果 `school_text` 为空，直接返回 `needs_clarification`，不访问数据库。
- 先查 `entity_aliases` 与 `edu_university` 的确认别名候选。
- 别名候选只有 1 个时，直接返回该学校。
- 别名候选超过 1 个时，返回 `needs_clarification` 和候选列表，不自动选择。
- 没有命中别名时，回退到 `edu_university`，按学校全称、code、school_id、别名子查询、short、name LIKE、old_name 检索；候选排序优先当前校名匹配，再考虑旧名匹配。
- fallback 命中多条候选且首条不是精确 `name`、`code` 或 `school_id` 时，返回 `needs_clarification`，不把第一条模糊候选当作已解析实体。

## 2. 输入与输出

- 主要输入：`school_text`，可选 `limit`。
- 关键输出：`selected_school`、`candidates`、`normalized_slots`。
- 来源字段：`source_tables` 应包含 `edu_university` 和 `entity_aliases`。
- 说明字段：`scope_notes`、`warnings`、`needs_clarification` 用于告诉上层 agent 是否可以直接使用结果。

## 3. 状态语义

- `ok`：唯一确认别名命中；或 fallback 精确命中学校全称、学校代码、内部 `school_id`；或 fallback 只返回一个可用候选。
- `not_found`：别名和学校基础表都没有命中。
- `needs_clarification`：缺少 `school_text`；输入命中多个确认别名候选；或 fallback 模糊检索命中多个非精确候选。
- `partial`：当前工具不使用该状态。

## 4. 测试范围

当前专属测试为离线单元测试，通过 `FakeClient` 控制 SQL 返回，不依赖真实 MySQL。已覆盖：

- 空输入和空白输入。
- 标准学校名、学校代码、内部 `school_id`。
- 唯一确认别名短路 fallback。
- 英文别名大小写和空白归一化。
- 非正式外号，如 `P大`、`SYSU`、`双鸭山大学`。
- 歧义简称，如 `中大`、`南大`、`交大`、`山大`、`河大`、`华工`、`华师`、`湖大`。
- 补充别名，如 `重邮`、`北工大`、`哈工`。
- `limit=1` 下歧义别名仍保留宽候选查询。
- 未命中不猜测。
- fallback 模糊多候选不直接选中第一条，例如 `科技大学`、`大`。
- fallback SQL 中的 `short`、`name LIKE`、`old_name`、别名子查询条件和当前校名优先于旧名的排序。
- 单引号输入的 SQL quote。

真实库审计另覆盖了 `华大`、`南理`、`科技大学`、`师范大学`、`医科大学`、`电子`、`交通`、`大学`、`大` 等高风险输入。修复后这些输入均返回 `needs_clarification`，不再返回危险 `ok`。

## 5. 测试结果

- 最近运行日期：2026-06-02
- 运行命令：`python -m pytest tests/function_calls/school_lookup tests/test_setup_entity_aliases.py tests/test_retrieval_tools.py tests/test_local_retrieval_mvp.py`
- 运行结果：`77 passed in 0.52s`
- 真实库验证：已运行 `scripts/setup_entity_aliases.py` 更新本地 `entity_aliases`；抽查 `重邮`、`北工大`、`哈工` 为 `ok`，`河大` 为 `needs_clarification`，上述高风险 fallback 输入均为 `needs_clarification`。2026-06-02 补充验证 `中国地质大学` 和 `师范` 的候选排序，当前校名匹配已排在旧名匹配前。

## 6. 已知风险与待改善

- 离线单元测试主要验证工具契约、SQL 生成路径和 FakeClient 下的行为；真实库质量仍需要定期审计。
- fallback 仍会返回较宽候选列表，但多候选已不再直接 `ok`；后续可继续优化候选排序和候选解释。
- 歧义候选依赖人工 seed，后续仍需从真实用户输入补充更多简称和地区上下文。
- 校区类口语输入仍依赖别名 seed；本轮已补 `电子科技大学沙河校区`、`哈工深`、`北邮宏福`、`人大苏州`、`山大威海` 等库内已有实体的常见说法。后续长尾校区仍需从真实问题继续补。
- raw 自然语言整句不属于 `school_lookup` 的职责；例如“孩子想去杭电”需要上层自然语言入口先抽槽为 `杭电`。

## 7. 关联文件

- 实现：[scripts/retrieval_tools.py](../../../scripts/retrieval_tools.py)
- SQL 构造：[scripts/local_retrieval_mvp.py](../../../scripts/local_retrieval_mvp.py)
- 别名 seed：[scripts/setup_entity_aliases.py](../../../scripts/setup_entity_aliases.py)
- 专属测试：[test_school_lookup_function_call.py](test_school_lookup_function_call.py)
- 能力边界审计：[reports/school_lookup_boundary_audit_20260602.md](../../../reports/school_lookup_boundary_audit_20260602.md)
