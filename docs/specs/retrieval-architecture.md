# 结构化检索架构说明

## 目标

本系统第一阶段先不做“万能联网问答”，而是基于现有 MySQL 数据库构建一个稳定、可解释、可标记缺口的结构化检索系统。

核心目标：

1. 优先使用已有结构化数据回答学生问题。
2. 明确区分“已有事实”“通用参考”“缺失数据”。
3. 不让模型直接编造学校、专业、薪资、就业、转专业、分流比例等高风险结论。
4. 把当前数据库答不了的问题记录为数据缺口，后续由联网 agent 补充。

## 总体链路

```text
用户问题
  -> 问题类型识别
  -> 学校/专业/省份/年份/批次实体识别
  -> 学校专业索引检索
  -> 按问题类型调用结构化查询
  -> 生成标准上下文包
  -> 判断缺失字段
  -> 生成回答或写入数据缺口队列
```

## 检索原则

### SQL 优先

能用结构化 SQL 精确查询的内容，优先走 MySQL，不走向量检索。

适合 SQL 查询的数据包括：

- 学校基础信息
- 专业基础信息
- 学校是否开设某专业
- 双一流标签
- 学科评估
- 招生计划
- 专业组
- 分数线
- 位次
- 学校级就业率、升学率、保研率

### 模型只负责理解和表达

模型可以做：

- 识别用户问题意图
- 识别学校、专业、省份、年份等实体
- 把结构化检索结果组织成自然语言
- 用清楚的话解释缺失项和不确定性

模型不可以做：

- 凭空补就业率
- 凭空补薪资分布
- 凭空补 Top 企业
- 凭空补转专业成功率
- 凭空补分流比例
- 把专业通用数据说成某校某专业数据

### 缺失即标记

如果数据库里没有某个字段，不要临时编答案。系统应该输出缺失说明，并写入 `data_gap_queue`。

## 第一版问题类型

### 1. 学校专业是否开设

示例：

```text
上海工程技术大学有机械工程吗？
```

主要数据源：

- `edu_school_major`
- `edu_university_department_major`
- `edu_university`
- `edu_major`

回答重点：

- 是否确认开设
- 专业代码
- 层次
- 学制
- 学位
- 数据来源表
- 如果只在扩展表命中，要提示置信度低于主索引

### 2. 学校专业浅层解读

示例：

```text
杭电自动化怎么样？
```

主要数据源：

- `school_major_index`
- `edu_university`
- `edu_major`
- `edu_school_major`
- `edu_dual_class`
- `edu_university_subject_eval`
- `edu_university_employment`

回答重点：

- 学校基本层次
- 专业基础介绍
- 专业学习内容
- 通用就业方向
- 学校级就业升学概况
- 学科评估或双一流情况
- 已缺失的数据

### 3. 学校就业升学概况

示例：

```text
这个学校就业和升学怎么样？
```

主要数据源：

- `edu_university_employment`

回答重点：

- 就业率
- 升学率
- 保研率
- 年份
- 来源提示
- 是否学校级数据

注意：

`edu_university_employment` 当前主要是学校级数据，不能直接替代某校某专业的就业数据。

### 4. 专业通用就业和薪资

示例：

```text
机械工程一般去哪些行业，薪资怎么样？
```

主要数据源：

- `edu_major`
- `edu_major_salary_trend`
- `edu_major_position_salary`

回答重点：

- 专业定义
- 学习内容
- 就业方向
- 通用就业地区
- 通用就业行业
- 通用薪资字段

注意：

专业通用薪资只能说“该专业整体参考”，不能说成某学校该专业毕业生薪资。

### 5. 专业组风险初筛

示例：

```text
这个专业组会不会被调剂到冷门专业？
```

主要数据源：

- `edu_college_specialty_group`
- `edu_specialty_group_major`
- `edu_university_plan_special_group`
- `edu_university_plan_special`
- `edu_university_score_group`
- `edu_university_score_special`

回答重点：

- 专业组包含哪些专业
- 每个专业计划人数
- 是否允许组内调剂
- 历史最低分和最低位次
- 是否存在明显低热度专业
- 当前是否缺少真实分流规则

注意：

招生专业组不等于入学后的大类分流。没有学校分流细则时，只能做风险初筛，不能输出确定分流比例。

### 6. 历年录取与招生计划

示例：

```text
这个专业去年最低位次多少？
```

主要数据源：

- `edu_university_plan_config`
- `edu_university_plan_special_group`
- `edu_university_plan_special`
- `edu_university_score_config`
- `edu_university_score_group`
- `edu_university_score_special`
- `edu_school_admission_stats`
- `edu_score_rank`

回答重点：

- 年份
- 省份
- 科类
- 批次
- 招生计划
- 最低分
- 最低位次
- 平均分或平均位次

### 7. 缺口识别

示例：

```text
这个专业毕业前 10 的对口公司有哪些？
```

如果当前库没有数据，应该输出：

- 当前数据库暂未覆盖该字段
- 已有可参考信息是什么
- 缺少的数据类型是什么
- 是否已进入补数队列

## 标准上下文包

所有检索接口最终都应该整理成统一结构，再交给模型生成回答。

```json
{
  "question_type": "school_major_overview",
  "entities": {
    "school": {
      "school_id": "10252",
      "school_name": "上海理工大学"
    },
    "major": {
      "major_code": "080202",
      "major_name": "机械设计制造及其自动化"
    },
    "province": null,
    "year": 2025
  },
  "facts": {
    "school": {},
    "major": {},
    "school_major": {},
    "employment": {},
    "admission": {},
    "specialty_group": {}
  },
  "data_gaps": [
    {
      "gap_type": "school_major_employment",
      "description": "缺少该校该专业单独就业地域、薪资和重点单位数据"
    }
  ],
  "warnings": [
    "当前薪资为专业通用数据，不代表该校该专业毕业生薪资"
  ]
}
```

## 回答格式

第一版回答建议固定为四段：

```text
1. 已确认的信息
2. 可参考的数据
3. 当前缺失的信息
4. 下一步可补充的信息
```

示例：

```text
目前可以确认，某校开设某专业，专业代码为 XXXX，属于 XX 类。

可参考数据方面，该专业通用就业方向包括 A、B、C；学校级就业率为 XX%，升学率为 XX%。

但当前数据库暂未覆盖该校该专业单独的就业地域分布、薪资分布和 Top 企业，因此不能把专业通用薪资当成该校该专业薪资。

该缺口可进入后续联网补数队列，优先检索学校就业质量报告、学院官网和招聘数据。
```

## 后续联网 Agent 位置

联网 agent 不直接面对用户，不临时生成最终答案。它只消费数据缺口队列，把缺失数据补回数据库。

推荐后续 agent：

- `SourceDiscoveryAgent`: 查找官网、就业报告、政策文件、招生章程。
- `CrawlerAgent`: 抓取网页和 PDF。
- `ExtractorAgent`: 抽取结构化字段。
- `VerifierAgent`: 校验来源等级、年份和冲突。
- `WriterAgent`: 写入事实表、来源表和缺口状态。
- `ManualReviewAgent`: 处理低置信度或来源冲突的数据。

## 第一阶段验收标准

第一阶段完成时，应满足：

1. 输入学校和专业名称，能判断是否开设。
2. 能返回学校基础信息和专业基础信息。
3. 能返回学校级就业升学信息。
4. 能返回专业通用就业和薪资信息。
5. 能返回专业组和录取相关信息。
6. 能明确标记专业级就业、转专业、分流比例、Top 企业、考公岗位等缺口。
7. 不能因缺数据而编造结论。
