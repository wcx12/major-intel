# school_major_list 边界审计报告

- 用例总数：36
- 通过：33
- 失败：3
- 需要复核：0

## 分类汇总

- input_validation_gap（输入校验缺口）：2
- limit_truncated（limit 正常截断）：1
- pass（通过）：32
- status_mismatch（状态不符合预期）：1

## 逐项结果

### hdu_all

- 输入：school=杭州电子科技大学, major_category=<none>, limit=100
- 判定：通过
- 分类：pass（通过）
- 原因：工具返回数量与参考查询一致。
- 工具结果：status=ok, 专业数=51
- 参考查询：筛选后专业数=51, 全部专业数=51
- 学校关联键分布：matches_code=8, matches_school_id=0, other=0
- 漏召回专业样本：-

### hdu_cs

- 输入：school=杭州电子科技大学, major_category=计算机, limit=50
- 判定：通过
- 分类：pass（通过）
- 原因：工具返回数量与参考查询一致。
- 工具结果：status=ok, 专业数=7
- 参考查询：筛选后专业数=7, 全部专业数=51
- 学校关联键分布：matches_code=8, matches_school_id=0, other=0
- 漏召回专业样本：-

### hdu_software

- 输入：school=杭州电子科技大学, major_category=软件工程, limit=20
- 判定：通过
- 分类：pass（通过）
- 原因：工具返回数量与参考查询一致。
- 工具结果：status=ok, 专业数=1
- 参考查询：筛选后专业数=1, 全部专业数=51
- 学校关联键分布：matches_code=8, matches_school_id=0, other=0
- 漏召回专业样本：-

### hdu_digital_media

- 输入：school=杭州电子科技大学, major_category=数字媒体技术, limit=20
- 判定：通过
- 分类：pass（通过）
- 原因：工具返回数量与参考查询一致。
- 工具结果：status=ok, 专业数=1
- 参考查询：筛选后专业数=1, 全部专业数=51
- 学校关联键分布：matches_code=8, matches_school_id=0, other=0
- 漏召回专业样本：-

### hdu_vocational_category_noise

- 输入：school=杭州电子科技大学, major_category=电子与信息大类, limit=20
- 判定：通过
- 分类：pass（通过）
- 原因：工具状态符合预期：not_found。
- 工具结果：status=not_found, 专业数=0
- 参考查询：筛选后专业数=0, 全部专业数=51
- 学校关联键分布：matches_code=8, matches_school_id=0, other=0
- 漏召回专业样本：-

### hdu_engineering

- 输入：school=杭州电子科技大学, major_category=工学, limit=50
- 判定：通过
- 分类：pass（通过）
- 原因：工具返回数量与参考查询一致。
- 工具结果：status=ok, 专业数=24
- 参考查询：筛选后专业数=24, 全部专业数=51
- 学校关联键分布：matches_code=8, matches_school_id=0, other=0
- 漏召回专业样本：-

### hdu_electronic_info

- 输入：school=杭州电子科技大学, major_category=电子信息类, limit=50
- 判定：通过
- 分类：pass（通过）
- 原因：工具返回数量与参考查询一致。
- 工具结果：status=ok, 专业数=7
- 参考查询：筛选后专业数=7, 全部专业数=51
- 学校关联键分布：matches_code=8, matches_school_id=0, other=0
- 漏召回专业样本：-

### beijing_language_all

- 输入：school=北京语言大学, major_category=<none>, limit=100
- 判定：通过
- 分类：pass（通过）
- 原因：工具返回数量与参考查询一致。
- 工具结果：status=ok, 专业数=40
- 参考查询：筛选后专业数=40, 全部专业数=40
- 学校关联键分布：matches_code=38, matches_school_id=0, other=0
- 漏召回专业样本：-

### beijing_language_cs

- 输入：school=北京语言大学, major_category=计算机, limit=50
- 判定：通过
- 分类：pass（通过）
- 原因：工具返回数量与参考查询一致。
- 工具结果：status=ok, 专业数=3
- 参考查询：筛选后专业数=3, 全部专业数=40
- 学校关联键分布：matches_code=38, matches_school_id=0, other=0
- 漏召回专业样本：-

### cqupt_all

- 输入：school=重庆邮电大学, major_category=<none>, limit=100
- 判定：通过
- 分类：pass（通过）
- 原因：工具返回数量与参考查询一致。
- 工具结果：status=ok, 专业数=55
- 参考查询：筛选后专业数=55, 全部专业数=55
- 学校关联键分布：matches_code=2, matches_school_id=16, other=0
- 漏召回专业样本：-

### cqupt_cs

- 输入：school=重庆邮电大学, major_category=计算机, limit=50
- 判定：通过
- 分类：pass（通过）
- 原因：工具返回数量与参考查询一致。
- 工具结果：status=ok, 专业数=8
- 参考查询：筛选后专业数=8, 全部专业数=55
- 学校关联键分布：matches_code=2, matches_school_id=16, other=0
- 漏召回专业样本：-

### cqupt_software

- 输入：school=重庆邮电大学, major_category=软件工程, limit=20
- 判定：通过
- 分类：pass（通过）
- 原因：工具返回数量与参考查询一致。
- 工具结果：status=ok, 专业数=1
- 参考查询：筛选后专业数=1, 全部专业数=55
- 学校关联键分布：matches_code=2, matches_school_id=16, other=0
- 漏召回专业样本：-

### cqupt_electronics

- 输入：school=重庆邮电大学, major_category=电子信息类, limit=50
- 判定：通过
- 分类：pass（通过）
- 原因：工具返回数量与参考查询一致。
- 工具结果：status=ok, 专业数=9
- 参考查询：筛选后专业数=9, 全部专业数=55
- 学校关联键分布：matches_code=2, matches_school_id=16, other=0
- 漏召回专业样本：-

### nuaa_all

- 输入：school=南京航空航天大学, major_category=<none>, limit=100
- 判定：通过
- 分类：pass（通过）
- 原因：工具返回数量与参考查询一致。
- 工具结果：status=ok, 专业数=63
- 参考查询：筛选后专业数=63, 全部专业数=63
- 学校关联键分布：matches_code=11, matches_school_id=27, other=0
- 漏召回专业样本：-

### nuaa_cs

- 输入：school=南京航空航天大学, major_category=计算机, limit=50
- 判定：通过
- 分类：pass（通过）
- 原因：工具返回数量与参考查询一致。
- 工具结果：status=ok, 专业数=4
- 参考查询：筛选后专业数=4, 全部专业数=63
- 学校关联键分布：matches_code=11, matches_school_id=27, other=0
- 漏召回专业样本：-

### nuaa_aerospace

- 输入：school=南京航空航天大学, major_category=航空航天, limit=50
- 判定：通过
- 分类：pass（通过）
- 原因：工具返回数量与参考查询一致。
- 工具结果：status=ok, 专业数=9
- 参考查询：筛选后专业数=9, 全部专业数=63
- 学校关联键分布：matches_code=11, matches_school_id=27, other=0
- 漏召回专业样本：-

### nankai_all

- 输入：school=南开大学, major_category=<none>, limit=100
- 判定：通过
- 分类：pass（通过）
- 原因：工具返回数量与参考查询一致。
- 工具结果：status=ok, 专业数=88
- 参考查询：筛选后专业数=88, 全部专业数=88
- 学校关联键分布：matches_code=36, matches_school_id=18, other=0
- 漏召回专业样本：-

### nankai_cs

- 输入：school=南开大学, major_category=计算机, limit=50
- 判定：通过
- 分类：pass（通过）
- 原因：工具返回数量与参考查询一致。
- 工具结果：status=ok, 专业数=7
- 参考查询：筛选后专业数=7, 全部专业数=88
- 学校关联键分布：matches_code=36, matches_school_id=18, other=0
- 漏召回专业样本：-

### nankai_math

- 输入：school=南开大学, major_category=数学, limit=50
- 判定：通过
- 分类：pass（通过）
- 原因：工具返回数量与参考查询一致。
- 工具结果：status=ok, 专业数=2
- 参考查询：筛选后专业数=2, 全部专业数=88
- 学校关联键分布：matches_code=36, matches_school_id=18, other=0
- 漏召回专业样本：-

### cupl_cs

- 输入：school=中国政法大学, major_category=计算机, limit=50
- 判定：通过
- 分类：pass（通过）
- 原因：工具和参考查询都未命中记录。
- 工具结果：status=not_found, 专业数=0
- 参考查询：筛选后专业数=0, 全部专业数=24
- 学校关联键分布：matches_code=21, matches_school_id=3, other=0
- 漏召回专业样本：-

### cupl_law

- 输入：school=中国政法大学, major_category=法学, limit=50
- 判定：通过
- 分类：pass（通过）
- 原因：工具返回数量与参考查询一致。
- 工具结果：status=ok, 专业数=7
- 参考查询：筛选后专业数=7, 全部专业数=24
- 学校关联键分布：matches_code=21, matches_school_id=3, other=0
- 漏召回专业样本：-

### cupl_politics

- 输入：school=中国政法大学, major_category=政治学, limit=50
- 判定：通过
- 分类：pass（通过）
- 原因：工具返回数量与参考查询一致。
- 工具结果：status=ok, 专业数=2
- 参考查询：筛选后专业数=2, 全部专业数=24
- 学校关联键分布：matches_code=21, matches_school_id=3, other=0
- 漏召回专业样本：-

### uestc_cs

- 输入：school=电子科技大学, major_category=计算机, limit=50
- 判定：通过
- 分类：pass（通过）
- 原因：工具返回数量与参考查询一致。
- 工具结果：status=ok, 专业数=6
- 参考查询：筛选后专业数=6, 全部专业数=51
- 学校关联键分布：matches_code=3, matches_school_id=0, other=0
- 漏召回专业样本：-

### uestc_electronics

- 输入：school=电子科技大学, major_category=电子信息类, limit=50
- 判定：通过
- 分类：pass（通过）
- 原因：工具返回数量与参考查询一致。
- 工具结果：status=ok, 专业数=10
- 参考查询：筛选后专业数=10, 全部专业数=51
- 学校关联键分布：matches_code=3, matches_school_id=0, other=0
- 漏召回专业样本：-

### jlu_cs

- 输入：school=吉林大学, major_category=计算机, limit=50
- 判定：通过
- 分类：pass（通过）
- 原因：工具返回数量与参考查询一致。
- 工具结果：status=ok, 专业数=6
- 参考查询：筛选后专业数=6, 全部专业数=124
- 学校关联键分布：matches_code=11, matches_school_id=0, other=0
- 漏召回专业样本：-

### jlu_law

- 输入：school=吉林大学, major_category=法学, limit=50
- 判定：通过
- 分类：pass（通过）
- 原因：工具返回数量与参考查询一致。
- 工具结果：status=ok, 专业数=8
- 参考查询：筛选后专业数=8, 全部专业数=124
- 学校关联键分布：matches_code=11, matches_school_id=0, other=0
- 漏召回专业样本：-

### taizhou_cs

- 输入：school=台州学院, major_category=计算机, limit=50
- 判定：通过
- 分类：pass（通过）
- 原因：工具返回数量与参考查询一致。
- 工具结果：status=ok, 专业数=3
- 参考查询：筛选后专业数=3, 全部专业数=52
- 学校关联键分布：matches_code=21, matches_school_id=0, other=0
- 漏召回专业样本：-

### taizhou_medical

- 输入：school=台州学院, major_category=临床医学, limit=50
- 判定：通过
- 分类：pass（通过）
- 原因：工具返回数量与参考查询一致。
- 工具结果：status=ok, 专业数=1
- 参考查询：筛选后专业数=1, 全部专业数=52
- 学校关联键分布：matches_code=21, matches_school_id=0, other=0
- 漏召回专业样本：-

### xinzhou_cs

- 输入：school=忻州师范学院, major_category=计算机, limit=50
- 判定：通过
- 分类：pass（通过）
- 原因：工具返回数量与参考查询一致。
- 工具结果：status=ok, 专业数=4
- 参考查询：筛选后专业数=4, 全部专业数=49
- 学校关联键分布：matches_code=10, matches_school_id=0, other=0
- 漏召回专业样本：-

### nanda_alias

- 输入：school=南大, major_category=<none>, limit=20
- 判定：通过
- 分类：pass（通过）
- 原因：工具状态符合预期：needs_clarification。
- 工具结果：status=needs_clarification, 专业数=0
- 参考查询：筛选后专业数=0, 全部专业数=0
- 学校关联键分布：-
- 漏召回专业样本：-

### jiaoda_alias

- 输入：school=交大, major_category=<none>, limit=20
- 判定：通过
- 分类：pass（通过）
- 原因：工具状态符合预期：needs_clarification。
- 工具结果：status=needs_clarification, 专业数=0
- 参考查询：筛选后专业数=0, 全部专业数=0
- 学校关联键分布：-
- 漏召回专业样本：-

### huada_alias

- 输入：school=华大, major_category=<none>, limit=20
- 判定：失败
- 分类：status_mismatch（状态不符合预期）
- 原因：工具状态不符合预期：期望 needs_clarification，实际 ok。
- 工具结果：status=ok, 专业数=20
- 参考查询：筛选后专业数=76, 全部专业数=76
- 学校关联键分布：matches_code=24, matches_school_id=24, other=5
- 漏召回专业样本：化学, 化学生物学, 天文学, 地球系统科学, 生物科学, 心理学, 统计学, 理论与应用力学, 工程力学, 机械工程

### random_school

- 输入：school=不存在大学测试样本999, major_category=<none>, limit=20
- 判定：通过
- 分类：pass（通过）
- 原因：工具状态符合预期：not_found。
- 工具结果：status=not_found, 专业数=0
- 参考查询：筛选后专业数=0, 全部专业数=0
- 学校关联键分布：-
- 漏召回专业样本：-

### cupl_limit_1

- 输入：school=中国政法大学, major_category=<none>, limit=1
- 判定：通过
- 分类：limit_truncated（limit 正常截断）
- 原因：工具按正数 limit 返回了指定条数；参考查询仍有更多记录。
- 工具结果：status=ok, 专业数=1
- 参考查询：筛选后专业数=24, 全部专业数=24
- 学校关联键分布：matches_code=21, matches_school_id=3, other=0
- 漏召回专业样本：经济学, 金融工程, 法学, 政治学与行政学, 国际政治, 社会学, 社会工作, 思想政治教育, 侦查学, 社会体育指导与管理

### cupl_limit_0

- 输入：school=中国政法大学, major_category=<none>, limit=0
- 判定：失败
- 分类：input_validation_gap（输入校验缺口）
- 原因：limit 小于 1 时仍返回普通检索结果，未给出参数校验提示。
- 工具结果：status=not_found, 专业数=0
- 参考查询：筛选后专业数=24, 全部专业数=24
- 学校关联键分布：matches_code=21, matches_school_id=3, other=0
- 漏召回专业样本：哲学, 经济学, 金融工程, 法学, 政治学与行政学, 国际政治, 社会学, 社会工作, 思想政治教育, 侦查学

### cupl_limit_negative

- 输入：school=中国政法大学, major_category=<none>, limit=-1
- 判定：失败
- 分类：input_validation_gap（输入校验缺口）
- 原因：limit 小于 1 时仍返回普通检索结果，未给出参数校验提示。
- 工具结果：status=error, 专业数=0
- 参考查询：筛选后专业数=0, 全部专业数=0
- 学校关联键分布：-
- 漏召回专业样本：-
