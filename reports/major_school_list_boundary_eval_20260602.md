# major_school_list 边界审计报告

- 用例总数：16
- 通过：16
- 失败：0
- 需要复核：0

## 分类汇总

- pass（通过）：16

## 逐项结果

### cs_zhejiang_undergrad_dual_key

- 输入：major=计算机科学与技术, province_filter=浙江, school_level_filter=本科, limit=30
- 判定：通过
- 分类：pass（通过）
- 原因：工具返回学校数量与参考查询一致。
- 工具结果：status=ok, 学校数=6
- 参考查询：学校数=6, 归一化省份=浙江
- 学校关联键分布：matches_code=2, matches_school_id=4, other=0
- 漏召回学校样本：-
- warnings：-
- data_gaps：-

### cs_nationwide_undergrad_dual_key

- 输入：major=计算机科学与技术, province_filter=<none>, school_level_filter=本科, limit=250
- 判定：通过
- 分类：pass（通过）
- 原因：工具返回学校数量与参考查询一致。
- 工具结果：status=ok, 学校数=195
- 参考查询：学校数=195, 归一化省份=<none>
- 学校关联键分布：matches_code=142, matches_school_id=65, other=0
- 漏召回学校样本：-
- warnings：-
- data_gaps：-

### cs_zhejiang_province_suffix

- 输入：major=计算机科学与技术, province_filter=浙江省, school_level_filter=本科, limit=30
- 判定：通过
- 分类：pass（通过）
- 原因：工具返回学校数量与参考查询一致。
- 工具结果：status=ok, 学校数=6
- 参考查询：学校数=6, 归一化省份=浙江
- 学校关联键分布：matches_code=2, matches_school_id=4, other=0
- 漏召回学校样本：-
- warnings：-
- data_gaps：-

### alias_jike_zhejiang_undergrad

- 输入：major=计科, province_filter=浙江, school_level_filter=本科, limit=30
- 判定：通过
- 分类：pass（通过）
- 原因：工具返回学校数量与参考查询一致。
- 工具结果：status=ok, 学校数=6
- 参考查询：学校数=6, 归一化省份=浙江
- 学校关联键分布：matches_code=2, matches_school_id=4, other=0
- 漏召回学校样本：-
- warnings：-
- data_gaps：-

### software_jiangsu_undergrad

- 输入：major=软件工程, province_filter=江苏, school_level_filter=本科, limit=50
- 判定：通过
- 分类：pass（通过）
- 原因：工具返回学校数量与参考查询一致。
- 工具结果：status=ok, 学校数=3
- 参考查询：学校数=3, 归一化省份=江苏
- 学校关联键分布：matches_code=2, matches_school_id=1, other=0
- 漏召回学校样本：-
- warnings：-
- data_gaps：-

### ai_shanghai_undergrad

- 输入：major=人工智能, province_filter=上海, school_level_filter=本科, limit=50
- 判定：通过
- 分类：pass（通过）
- 原因：工具和参考查询都未命中学校记录。
- 工具结果：status=not_found, 学校数=0
- 参考查询：学校数=0, 归一化省份=上海
- 学校关联键分布：matches_code=0, matches_school_id=0, other=0
- 漏召回学校样本：-
- warnings：本地库未命中开设该专业的学校记录。
- data_gaps：开设该专业的学校记录

### law_beijing_undergrad

- 输入：major=法学, province_filter=北京, school_level_filter=本科, limit=50
- 判定：通过
- 分类：pass（通过）
- 原因：工具返回学校数量与参考查询一致。
- 工具结果：status=ok, 学校数=12
- 参考查询：学校数=12, 归一化省份=北京
- 学校关联键分布：matches_code=10, matches_school_id=4, other=0
- 漏召回学校样本：-
- warnings：-
- data_gaps：-

### clinical_zhejiang_undergrad

- 输入：major=临床医学, province_filter=浙江, school_level_filter=本科, limit=50
- 判定：通过
- 分类：pass（通过）
- 原因：工具返回学校数量与参考查询一致。
- 工具结果：status=ok, 学校数=7
- 参考查询：学校数=7, 归一化省份=浙江
- 学校关联键分布：matches_code=6, matches_school_id=1, other=0
- 漏召回学校样本：-
- warnings：同名专业存在多个层次，当前默认优先普通本科专业代码；如需专科或职业本科，请提供专业代码。
- data_gaps：-

### cs_zhejiang_985_empty

- 输入：major=计算机科学与技术, province_filter=浙江, school_level_filter=985, limit=20
- 判定：通过
- 分类：pass（通过）
- 原因：工具和参考查询都未命中学校记录。
- 工具结果：status=not_found, 学校数=0
- 参考查询：学校数=0, 归一化省份=浙江
- 学校关联键分布：matches_code=0, matches_school_id=0, other=0
- 漏召回学校样本：-
- warnings：本地库未命中开设该专业的学校记录。
- data_gaps：开设该专业的学校记录

### cs_zhejiang_dual_empty

- 输入：major=计算机科学与技术, province_filter=浙江, school_level_filter=双一流, limit=20
- 判定：通过
- 分类：pass（通过）
- 原因：工具和参考查询都未命中学校记录。
- 工具结果：status=not_found, 学校数=0
- 参考查询：学校数=0, 归一化省份=浙江
- 学校关联键分布：matches_code=0, matches_school_id=0, other=0
- 漏召回学校样本：-
- warnings：本地库未命中开设该专业的学校记录。
- data_gaps：开设该专业的学校记录

### broad_computer_needs_clarification

- 输入：major=计算机, province_filter=浙江, school_level_filter=本科, limit=30
- 判定：通过
- 分类：pass（通过）
- 原因：工具状态符合预期：needs_clarification。
- 工具结果：status=needs_clarification, 学校数=0
- 参考查询：学校数=0, 归一化省份=浙江
- 学校关联键分布：-
- 漏召回学校样本：-
- warnings：专业输入命中多个候选，请提供专业全称或专业代码后再查询。
- data_gaps：-

### major_not_found

- 输入：major=不存在专业ABC, province_filter=浙江, school_level_filter=本科, limit=30
- 判定：通过
- 分类：pass（通过）
- 原因：工具状态符合预期：not_found。
- 工具结果：status=not_found, 学校数=0
- 参考查询：学校数=0, 归一化省份=浙江
- 学校关联键分布：-
- 漏召回学校样本：-
- warnings：本地库未命中专业实体，不能猜测专业。
- data_gaps：-

### invalid_province

- 输入：major=计算机科学与技术, province_filter=火星, school_level_filter=本科, limit=30
- 判定：通过
- 分类：pass（通过）
- 原因：工具和参考查询都未命中学校记录。
- 工具结果：status=not_found, 学校数=0
- 参考查询：学校数=0, 归一化省份=火星
- 学校关联键分布：matches_code=0, matches_school_id=0, other=0
- 漏召回学校样本：-
- warnings：本地库未命中开设该专业的学校记录。
- data_gaps：开设该专业的学校记录

### ecommerce_cross_level_warning

- 输入：major=电子商务, province_filter=浙江, school_level_filter=本科, limit=20
- 判定：通过
- 分类：pass（通过）
- 原因：工具返回学校数量与参考查询一致。
- 工具结果：status=ok, 学校数=2
- 参考查询：学校数=2, 归一化省份=浙江
- 学校关联键分布：matches_code=1, matches_school_id=1, other=0
- 漏召回学校样本：-
- warnings：同名专业存在多个层次，当前默认优先普通本科专业代码；如需专科或职业本科，请提供专业代码。
- data_gaps：-

### limit_zero

- 输入：major=计算机科学与技术, province_filter=浙江, school_level_filter=本科, limit=0
- 判定：通过
- 分类：pass（通过）
- 原因：limit 小于 1 时已返回结构化参数澄清，没有进入 SQL 层。
- 工具结果：status=needs_clarification, 学校数=0
- 参考查询：学校数=0, 归一化省份=浙江
- 学校关联键分布：-
- 漏召回学校样本：-
- warnings：limit 必须是正整数，不能进入 SQL 层。
- data_gaps：-

### limit_negative

- 输入：major=计算机科学与技术, province_filter=浙江, school_level_filter=本科, limit=-1
- 判定：通过
- 分类：pass（通过）
- 原因：limit 小于 1 时已返回结构化参数澄清，没有进入 SQL 层。
- 工具结果：status=needs_clarification, 学校数=0
- 参考查询：学校数=0, 归一化省份=浙江
- 学校关联键分布：-
- 漏召回学校样本：-
- warnings：limit 必须是正整数，不能进入 SQL 层。
- data_gaps：-
