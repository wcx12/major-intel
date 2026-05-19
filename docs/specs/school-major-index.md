# 学校专业索引设计

## 目标

`school_major_index` 是第一版检索系统的核心索引，用于回答：

```text
某学校是否开设某专业？
这个学校专业组合目前有哪些可用信息？
哪些信息已经有结构化数据？
哪些信息还需要后续 agent 补充？
```

这个索引不是替代原始表，而是把现有 MySQL 数据整理成更适合问答检索的统一视图或物化表。

## 主要来源表

### 主来源

`edu_school_major`

用途：

- 学校与专业的确认关系
- 专业代码
- 专业名称
- 学历层次
- 是否双一流专业
- 是否国家级一流本科专业
- 学科评估等级
- 专业门类和专业类

这个表应该作为第一版“学校开设专业”的主索引来源。

### 扩展来源

`edu_university_department_major`

用途：

- 补充更多学校专业组合
- 补充院系信息
- 补充学校专业关联关系

注意：

该表数据量更大，但 `special_id` 可能不是全国统一专业 ID。使用时应优先通过 `major_code + major_name + school_id` 去重和归一。

### 学校信息来源

`edu_university`

用途：

- 学校名称
- 省份
- 城市
- 学校层次
- 学校类型
- 公办/民办
- 985/211/双一流
- 主管部门
- 学校官网
- 招生网站
- 学校简介

### 专业信息来源

`edu_major`

用途：

- 专业代码
- 专业名称
- 专业门类
- 专业类
- 学制
- 学位
- 专业介绍
- 学习内容
- 就业方向
- 通用就业地区
- 通用就业行业
- 通用薪资

### 学科和荣誉来源

相关表：

- `edu_dual_class`
- `edu_university_subject_eval`
- `edu_college_label`
- `edu_college_rank`

用途：

- 双一流建设学科
- 学科评估等级
- 学校标签
- 学校排名

### 就业升学来源

`edu_university_employment`

用途：

- 学校级就业率
- 学校级升学率
- 保研率
- 就业质量报告链接
- 就业/升学备注

注意：

该表当前主要是学校级数据，不能直接视为某校某专业数据。

## 建议字段

```text
id
school_id
school_code
school_name
province_id
province_name
city_name
school_level
school_type_name
school_nature_name
is_985
is_211
is_dual_class_school
school_site
admission_site

major_code
major_name
special_id
major_level_name
degree_level
limit_year
degree
level2_code
level2_name
level3_code
level3_name

is_dual_class_major
is_national_first_class
is_national_feature
subject_eval_level
subject_eval_round

major_intro_available
major_job_available
major_salary_available
school_employment_available
school_employment_year

source_priority
source_tables
confidence_level
created_at
updated_at
```

## 字段解释

### `source_priority`

表示该学校专业关系来自哪个层级。

建议取值：

```text
1 = edu_school_major 主表确认
2 = edu_university_department_major 扩展表确认
3 = 招生计划或专业组反推确认
```

查询时优先使用 `source_priority = 1`。

### `source_tables`

记录该索引行由哪些表合并得到。

示例：

```json
["edu_school_major", "edu_university", "edu_major", "edu_university_employment"]
```

### `confidence_level`

建议取值：

```text
high
medium
low
```

规则：

- `high`: `edu_school_major` 命中，且能关联 `edu_university` 和 `edu_major`。
- `medium`: `edu_university_department_major` 命中，且能用 `major_code` 关联专业基础库。
- `low`: 仅从招生计划、专业组或文本字段中反推出学校专业关系。

## 去重规则

优先级：

1. `school_id + major_code`
2. `school_id + major_name`
3. `school_name + major_code`
4. `school_name + major_name`

如果同一个学校专业组合出现多条：

1. 优先保留 `edu_school_major` 来源。
2. 若 `major_code` 相同但 `major_name` 略有差异，保留标准专业库名称，同时记录原始名称。
3. 若 `major_name` 包含方向、实验班、中外合作等，应记录到扩展字段，不要覆盖标准专业名称。

示例：

```text
软件工程
软件工程（中外合作办学）
软件工程（卓越工程师班）
```

这三类不能简单合并为同一条业务含义。

## 与原始表的关系

`school_major_index` 应该是派生表或视图，不直接替代原表。

原始表仍然保留：

- 数据源追溯
- 字段补充
- 后续重新生成索引

推荐实现方式：

第一阶段可以先做数据库视图：

```text
v_school_major_index
```

如果查询性能不足，再做物化表：

```text
school_major_index
```

## 检索命中策略

### 用户输入学校和专业

流程：

```text
用户问题
  -> 学校别名匹配
  -> 专业别名匹配
  -> school_major_index 精确查询
  -> 如果未命中，尝试专业名称模糊匹配
  -> 如果仍未命中，查扩展表或写入缺口队列
```

### 学校命中但专业未命中

回答：

```text
当前数据库未确认该校开设该专业。可能原因包括：专业名称存在方向差异、招生名称与标准专业名称不一致，或当前库未覆盖。该问题应进入人工或联网补数队列。
```

### 专业命中但学校未命中

回答：

```text
当前数据库未识别到该学校。请确认学校全称，或进入学校别名补充流程。
```

## 需要避免的问题

### 不要把专业类当专业

例如：

```text
计算机类
机械类
电子信息类
```

这些可能是招生专业类，不一定是最终本科专业。

### 不要把招生专业组当入学后分流结果

专业组用于志愿填报和录取，不等于学生入学后的专业分流比例。

### 不要把通用专业薪资当学校专业薪资

`edu_major` 的薪资字段可以作为专业通用参考，但不能代表某校某专业毕业生薪资。

### 不要把学校级就业率当专业级就业率

`edu_university_employment` 目前主要是学校级就业升学数据。

## 第一版验收标准

索引完成后，应能支持：

1. 输入学校全称 + 专业名称，返回是否开设。
2. 输入学校简称 + 专业简称，经过别名解析后命中索引。
3. 返回学校基础信息和专业基础信息。
4. 返回数据置信度和来源表。
5. 标记专业级就业、转专业、分流比例、Top 企业等是否缺失。
6. 对未命中的学校专业组合，不直接否定，而是提示“当前数据库未确认”。
