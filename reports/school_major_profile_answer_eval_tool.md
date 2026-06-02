# school_major_profile Answer Evaluation

- Total: 8
- Passed: 8
- Failed: 0

## hdu_cs_no_context_ok

- Status: PASS
- Question: 杭电计算机怎么样？
- Tool status: ok
- Evidence summary: `{"has_primary_catalog": false, "has_department_catalog": true, "has_admission_or_plan": true, "has_admission_history": true, "has_plan": true, "has_specialty_group": true, "has_context_match": false, "evidence_count": 26, "matched_evidence_count": 24, "related_evidence_count": 0, "source_tables": ["edu_school_admission_stats", "edu_specialty_group_major", "edu_university_department_major", "edu_university_plan_special"]}`
- Warnings: 无
- Data gaps: 校专业级工作地域分布；校专业级薪资分布；校专业级Top对口公司；考公岗位映射；转专业政策；专业组真实分流比例/冷门专业比例；学校官网专业介绍证据链

Tool trace:
- `school_major_profile` status=`ok` args=`{"school_text": "杭州电子科技大学", "major_text": "计算机科学与技术"}`

## hdu_cs_zj_physics_2025_partial

- Status: PASS
- Question: 浙江物理2025年，杭电计算机怎么样？
- Tool status: partial
- Evidence summary: `{"has_primary_catalog": false, "has_department_catalog": true, "has_admission_or_plan": false, "has_admission_history": false, "has_plan": false, "has_specialty_group": false, "has_context_match": false, "evidence_count": 5, "matched_evidence_count": 0, "related_evidence_count": 3, "source_tables": ["edu_school_admission_stats", "edu_university_department_major"]}`
- Warnings: 已命中院系专业目录证据，但未命中该省份/科类/年份招生或录取证据。；命中了学校/专业相关招生或计划证据，但与请求的省份/科类/年份不完全匹配，不能作为该上下文结论。
- Data gaps: 校专业级工作地域分布；校专业级薪资分布；校专业级Top对口公司；考公岗位映射；转专业政策；专业组真实分流比例/冷门专业比例；学校官网专业介绍证据链

Tool trace:
- `school_major_profile` status=`partial` args=`{"school_text": "杭州电子科技大学", "major_text": "计算机科学与技术", "province": "浙江", "subject_type": "物理", "year": 2025}`

## hdu_cs_zj_comprehensive_2025_ok

- Status: PASS
- Question: 浙江综合2025年，杭电计算机怎么样？
- Tool status: ok
- Evidence summary: `{"has_primary_catalog": false, "has_department_catalog": true, "has_admission_or_plan": true, "has_admission_history": true, "has_plan": false, "has_specialty_group": false, "has_context_match": true, "evidence_count": 5, "matched_evidence_count": 3, "related_evidence_count": 0, "source_tables": ["edu_school_admission_stats", "edu_university_department_major"]}`
- Warnings: 无
- Data gaps: 校专业级工作地域分布；校专业级薪资分布；校专业级Top对口公司；考公岗位映射；转专业政策；专业组真实分流比例/冷门专业比例；学校官网专业介绍证据链

Tool trace:
- `school_major_profile` status=`ok` args=`{"school_text": "杭州电子科技大学", "major_text": "计算机科学与技术", "province": "浙江", "subject_type": "综合", "year": 2025}`

## hdu_cs_gd_physics_2025_context_code

- Status: PASS
- Question: 广东物理2025年，杭电计算机怎么样？
- Tool status: ok
- Evidence summary: `{"has_primary_catalog": false, "has_department_catalog": true, "has_admission_or_plan": true, "has_admission_history": false, "has_plan": true, "has_specialty_group": false, "has_context_match": true, "evidence_count": 3, "matched_evidence_count": 1, "related_evidence_count": 0, "source_tables": ["edu_university_department_major", "edu_university_plan_special"]}`
- Warnings: 无
- Data gaps: 校专业级工作地域分布；校专业级薪资分布；校专业级Top对口公司；考公岗位映射；转专业政策；专业组真实分流比例/冷门专业比例；学校官网专业介绍证据链

Tool trace:
- `school_major_profile` status=`ok` args=`{"school_text": "杭州电子科技大学", "major_text": "计算机科学与技术", "province": "广东", "subject_type": "物理", "year": 2025}`

## hdu_cs_gd_invalid_subject_2025_context_mismatch

- Status: PASS
- Question: 广东火星科2025年，杭电计算机怎么样？
- Tool status: needs_clarification
- Evidence summary: `{"has_primary_catalog": false, "has_department_catalog": false, "has_admission_or_plan": false, "has_admission_history": false, "has_plan": false, "has_specialty_group": false, "has_context_match": false, "evidence_count": 0, "matched_evidence_count": 0, "related_evidence_count": 0, "source_tables": []}`
- Warnings: 输入科类“火星科”不在本地支持范围内，请使用物理、历史、综合、理科、文科、艺术类或体育类。
- Data gaps: 校专业级工作地域分布；校专业级薪资分布；校专业级Top对口公司；考公岗位映射；转专业政策；专业组真实分流比例/冷门专业比例；学校官网专业介绍证据链

Tool trace:
- `school_major_profile` status=`needs_clarification` args=`{"school_text": "杭州电子科技大学", "major_text": "计算机科学与技术", "province": "广东", "subject_type": "火星科", "year": 2025}`

## hdu_nursing_unsafe_combo

- Status: PASS
- Question: 杭电护理学怎么样？
- Tool status: partial
- Evidence summary: `{"has_primary_catalog": false, "has_department_catalog": false, "has_admission_or_plan": false, "has_admission_history": false, "has_plan": false, "has_specialty_group": false, "has_context_match": false, "evidence_count": 0, "matched_evidence_count": 0, "related_evidence_count": 0, "source_tables": []}`
- Warnings: 本地库未命中院系专业目录证据，不能直接认定已开设。
- Data gaps: 校专业级工作地域分布；校专业级薪资分布；校专业级Top对口公司；考公岗位映射；转专业政策；专业组真实分流比例/冷门专业比例；学校官网专业介绍证据链

Tool trace:
- `school_major_profile` status=`partial` args=`{"school_text": "杭州电子科技大学", "major_text": "护理学"}`

## hdu_unknown_major_not_found

- Status: PASS
- Question: 杭电星际航道规划与管理怎么样？
- Tool status: not_found
- Evidence summary: `{"has_primary_catalog": false, "has_department_catalog": false, "has_admission_or_plan": false, "has_admission_history": false, "has_plan": false, "has_specialty_group": false, "has_context_match": false, "evidence_count": 0, "matched_evidence_count": 0, "related_evidence_count": 0, "source_tables": []}`
- Warnings: 未映射到标准专业库，已按招生计划/录取历史原始专业名称检索。；本地库未命中院系专业目录证据，不能直接认定已开设。
- Data gaps: 校专业级工作地域分布；校专业级薪资分布；校专业级Top对口公司；考公岗位映射；转专业政策；专业组真实分流比例/冷门专业比例；学校官网专业介绍证据链

Tool trace:
- `school_major_profile` status=`not_found` args=`{"school_text": "杭州电子科技大学", "major_text": "星际航道规划与管理"}`

## unknown_school_not_found

- Status: PASS
- Question: 不存在大学测试样本999计算机怎么样？
- Tool status: not_found
- Evidence summary: `{}`
- Warnings: 本地库未命中学校实体，不能猜测学校。
- Data gaps: 无

Tool trace:
- `school_major_profile` status=`not_found` args=`{"school_text": "不存在大学测试样本999", "major_text": "计算机科学与技术"}`
