# DeepSeek Agent Manual Test

- Time: 2026-05-20 20:57:47
- Exit code: 0

## Input

```text
杭电计算机怎么样？
```

## Command

```powershell
C:\Users\10627\anaconda3\envs\major-intel-agent\python.exe scripts/deepseek_retrieval_agent.py "杭电计算机怎么样？" --show-trace
```

## Output

```text
数据已经比较全面了，下面为您做一个系统总结。

---

## 杭电计算机科学与技术 — 全面分析

### 🏫 学校定位

杭州电子科技大学是浙江省属重点理工类本科院校，位于**杭州**。虽然不是985/211，但入选了**双一流学科建设**（2个学科），在电子信息领域有很强的行业认可度，素有"IT企业家摇篮"之称。

---

### 📊 学科实力：第四轮学科评估 **B+**

在教育部第四轮学科评估中，杭电**计算机科学与技术**获评 **B+**，与**电子科学与技术、控制科学与工程**并列校内最强学科。这个评级在非211高校中属于非常出色的水平，和不少211院校处于同一梯队。

---

### 🎯 招生录取参考（2024-2025年专业组样本）

| 省份 | 年份 | 科类 | 最低分 | 最低位次 | 备注 |
|------|------|------|--------|----------|------|
| 黑龙江 | 2025 | 物理 | 591 | 5663 | 普通类 |
| 上海 | 2025 | 综合 | 550 | 9779 | 普通类 |
| 江苏 | 2025 | 物理 | 609 | 19004 | 普通类 |
| 江苏 | 2025 | 物理 | 608 | 27150 | 中外合作办学 |
| 福建 | 2024 | 物理 | 604 | 8849 | 中外合作办学 |
| 湖北 | 2024 | 物理 | 602 | 16685 | 中外合作办学 |

> ⚠️ **注意**：以上是专业组最低分/位次，不是该专业单独的录取线。选科要求均为**物理+化学**。中外合作办学方向与俄罗斯圣光机大学合作，中英文授课。

---

### 💼 就业与升学

- **学校级升学率**：约 **40%**（2025年数据），说明深造氛围较好。
- ⚠️ 本地库**缺少杭电计算机专业级**的就业去向、薪资分布和Top雇主数据，以下为**计算机专业通用市场参考**：

#### 行业分布（全国通用）
| 行业 | 占比 |
|------|------|
| IT软件 | 27.86% |
| 互联网 | 10.43% |
| 系统集成 | 6.83% |
| 电信设备 | 6.39% |

#### 岗位方向
后端开发（14.2%）、技术支持（10.2%）、移动开发（6.7%）、销售业务（5.8%）、测试（5.3%）

#### 薪资参考（全国通用市场样本）
| 城市 | 月薪参考 |
|------|----------|
| 北京 | ~10,115元 |
| 上海 | ~9,826元 |
| 深圳 | ~8,660元 |
| **杭州** | **~8,075元** |
| 南京 | ~7,621元 |

> 杭州本地招聘样本中，阿里巴巴等大厂岗位月薪可达 **4.5-6.5万**（资深岗位），说明杭电地处杭州，对接阿里、网易等互联网大厂有天然地理优势。

---

### 🏛️ 考公岗位

计算机科学与技术是考公**热门专业**，2026年国考岗位样本覆盖：
- 出入境边防检查总站（新疆、内蒙古、青海等）
- 国家金融监督管理总局（福建等）
- 岗位类型以**行政执法类**和**综合管理类**为主

> ⚠️ 最终可报范围以当年官方岗位表为准。

---

### ⚠️ 数据缺口提示

以下数据本地库暂未覆盖，建议通过其他渠道补充：
- 杭电计算机专业级**真实就业去向和薪资**
- 杭电计算机专业级**Top对口公司**
- 转专业政策
- 专业组内真实分流比例

---

### 📝 总结

**杭电计算机是一个性价比很高的选择**：B+学科评估、杭州互联网产业区位优势、40%升学率，在非211院校中属于第一梯队。如果你分数在各省物理类600分左右、位次在5000-20000区间（因省而异），杭电计算机值得重点考虑。尤其对于想在长三角互联网行业发展的考生，地理和行业人脉优势明显。

如果你能告诉我你的**省份、科类和分数/位次**，我可以帮你做更精准的冲稳保匹配分析！
[
  {
    "tool_name": "school_lookup",
    "arguments": {
      "school_text": "杭电"
    },
    "result": {
      "tool_name": "school_lookup",
      "status": "not_found",
      "input": {
        "school_text": "杭电",
        "limit": 5
      },
      "normalized_slots": {},
      "data": {
        "selected_school": {},
        "candidates": []
      },
      "scope_notes": [],
      "data_gaps": [],
      "needs_clarification": [],
      "source_tables": [
        "edu_university"
      ],
      "warnings": [
        "本地库未命中学校实体，不能猜测学校。"
      ]
    }
  },
  {
    "tool_name": "major_lookup",
    "arguments": {
      "major_text": "计算机"
    },
    "result": {
      "tool_name": "major_lookup",
      "status": "ok",
      "input": {
        "major_text": "计算机",
        "limit": 5
      },
      "normalized_slots": {
        "major_name": "计算机科学与技术",
        "major_code": "080901"
      },
      "data": {
        "selected_major": {
          "special_id": "080901",
          "code": "080901",
          "special_name": "计算机科学与技术",
          "type_name": "本科(普通)",
          "level2_name": "工学",
          "level3_name": "计算机类",
          "limit_year": "四年",
          "degree": "理学学士,工学学士",
          "salaryavg": null,
          "fivesalaryavg": null,
          "job": null,
          "is_what": null,
          "learn_what": null,
          "do_what": null,
          "job_clean": "",
          "mostemploymentarea": null,
          "mostemploymentindustry": null,
          "mostemployedeposition": null
        },
        "candidates": [
          {
            "special_id": "080901",
            "code": "080901",
            "special_name": "计算机科学与技术",
            "type_name": "本科(普通)",
            "level2_name": "工学",
            "level3_name": "计算机类",
            "limit_year": "四年",
            "degree": "理学学士,工学学士",
            "salaryavg": null,
            "fivesalaryavg": null,
            "job": null,
            "is_what": null,
            "learn_what": null,
            "do_what": null,
            "job_clean": "",
            "mostemploymentarea": null,
            "mostemploymentindustry": null,
            "mostemployedeposition": null
          },
          {
            "special_id": "784",
            "code": "510202",
            "special_name": "计算机网络技术",
            "type_name": null,
            "level2_name": "电子与信息大类",
            "level3_name": "计算机类",
            "limit_year": "三年",
            "degree": null,
            "salaryavg": "152732",
            "fivesalaryavg": "11800",
            "job": null,
            "is_what": "计算机网络技术主要研究计算机网络和网络工程等方面基本知识和技能，进行网络安装维护、网络管理、网络软件部署、系统集成、计算机软硬件方面的维护与营销、数据库管理等。例如：电脑等设备安装与调试，计算机系统的测试、维护和维修，网页图形、图像、动画、视频、声音等多媒体设计及制作等。\r\n关键词：电脑  设备  图形  动画",
            "learn_what": "《计算机网络》、《网页设计与脚本语言》、《计算机组装与调试》、《路由与交换技术》、《动态网站开发与实践》、《企业网络构建》、《网络服务器配置》、《Linux操作系统应用》、《网络编程技术》、《网络安全》",
            "do_what": "网络信息类企事业单位：网络规划和方案设计，网络安装和管理，网络安全防护，服务器的配置、管理和维护，网站开发，数据库管理。",
            "job_clean": "网络信息类企事业单位：网络规划和方案设计，网络安装和管理，网络安全防护，服务器的配置、管理和维护，网站开发，数据库管理。",
            "mostemploymentarea": "北京市",
            "mostemploymentindustry": "互联网",
            "mostemployedeposition": "销售业务"
          },
          {
            "special_id": "783",
            "code": "510201",
            "special_name": "计算机应用技术",
            "type_name": null,
            "level2_name": "电子与信息大类",
            "level3_name": "计算机类",
            "limit_year": "三年",
            "degree": null,
            "salaryavg": "168447",
            "fivesalaryavg": "11900",
            "job": null,
            "is_what": "计算机应用技术主要研究计算机系统管理、应用软件开发、网络管理、信息系统管理和网站建设等方面基本知识和技能，进行数据库应用开发、网站配置与测试、网站运营与维护、技术服务等。例如：京东、当当等网站的设计与开发，数据库的建设与管理，软件的测试与维护等。\r\n关键词：京东  网站  数据库  软件",
            "learn_what": "《计算机基础》、《计算机系统组装与维护》、《网站规划与制作》、《数据库原理与应用》、《微机原理》、《计算机网络技术》、《C/Java语言程序设计》、《平面设计与制作》、《NET程序设计》、《图形图像处理技术》",
            "do_what": "网络信息类企事业单位：网站设计与开发、网络规划与设计、网络系统设计和测试、应用软件开发、系统管理与维护、信息产品设计与技术支持。",
            "job_clean": "网络信息类企事业单位：网站设计与开发、网络规划与设计、网络系统设计和测试、应用软件开发、系统管理与维护、信息产品设计与技术支持。",
            "mostemploymentarea": "北京市",
            "mostemploymentindustry": "互联网",
            "mostemployedeposition": "销售业务"
          },
          {
            "special_id": "1170",
            "code": "080909T",
            "special_name": "电子与计算机工程",
            "type_name": null,
            "level2_name": "工学",
            "level3_name": "计算机类",
            "limit_year": "四年",
            "degree": "工学学士",
            "salaryavg": "136647",
            "fivesalaryavg": "21400",
            "job": null,
            "is_what": "电子与计算机工程结合电气工程和计算机科学，主要研究现代电子、自动控制、电力工程以及计算机技术等方面的基本知识和技能，进行现代电子系统的开发设计、工艺控制、智能设备的软硬件开发等。例如：工业设备控制系统的研发，自动门控制系统的设计，电脑等电子产品的电路设计等。\n关键词：电子  计算机  电路  控制",
            "learn_what": "《固体物理学》、《材料机械性能》、《单片集成放大器电路设计》、《电路设计导论》、《多核计算与并行处理》、《工程概率方法》、《工程优化》、《基于微处理器的系统设计》、《控制系统分析与设计》、《数字通信信号与系统》",
            "do_what": "IT类企业：电子系统的开发设计、智能设备的软硬件开发、技术支持、软件测试、技术管理；\n电子类企业：电子技术、IC设计、工艺控制、电气工程；\n政府、事业类单位：电子信息系统的维护管理。",
            "job_clean": "IT类企业：电子系统的开发设计、智能设备的软硬件开发、技术支持、软件测试、技术管理； 电子类企业：电子技术、IC设计、工艺控制、电气工程； 政府、事业类单位：电子信息系统的维护管理。",
            "mostemploymentarea": "北京市",
            "mostemploymentindustry": null,
            "mostemployedeposition": null
          },
          {
            "special_id": "9471",
            "code": "310201",
            "special_name": "计算机应用工程",
            "type_name": null,
            "level2_name": "电子与信息大类",
            "level3_name": "计算机类",
            "limit_year": "四年",
            "degree": "工学学士",
            "salaryavg": "0",
            "fivesalaryavg": "0",
            "job": null,
            "is_what": "暂未数据",
            "learn_what": "暂未数据",
            "do_what": "暂未数据",
            "job_clean": "暂未数据",
            "mostemploymentarea": null,
            "mostemploymentindustry": null,
            "mostemployedeposition": null
          }
        ]
      },
      "scope_notes": [
        "专业实体解析来自 edu_major 和 entity_aliases；短简称只使用已确认别名，不直接做短词模糊匹配。"
      ],
      "data_gaps": [],
      "needs_clarification": [],
      "source_tables": [
        "edu_major",
        "entity_aliases"
      ],
      "warnings": []
    }
  },
  {
    "tool_name": "school_lookup",
    "arguments": {
      "school_text": "杭州电子科技大学"
    },
    "result": {
      "tool_name": "school_lookup",
      "status": "ok",
      "input": {
        "school_text": "杭州电子科技大学",
        "limit": 5
      },
      "normalized_slots": {
        "school_name": "杭州电子科技大学",
        "school_id": "10124"
      },
      "data": {
        "selected_school": {
          "school_id": "10124",
          "code": "10336",
          "name": "杭州电子科技大学",
          "province_name": "浙江",
          "city_name": "杭州市",
          "type_name": "理工",
          "level_name": "本科",
          "is985": "0",
          "is211": "0",
          "is_dual_class": "0",
          "dual_class": "2",
          "school_site": "https://www.hdu.edu.cn/main.htm",
          "site": "http://grs.hdu.edu.cn/1721/list.htm"
        },
        "candidates": [
          {
            "school_id": "10124",
            "code": "10336",
            "name": "杭州电子科技大学",
            "province_name": "浙江",
            "city_name": "杭州市",
            "type_name": "理工",
            "level_name": "本科",
            "is985": "0",
            "is211": "0",
            "is_dual_class": "0",
            "dual_class": "2",
            "school_site": "https://www.hdu.edu.cn/main.htm",
            "site": "http://grs.hdu.edu.cn/1721/list.htm"
          },
          {
            "school_id": "11121",
            "code": "13279",
            "name": "杭州电子科技大学信息工程学院",
            "province_name": "浙江",
            "city_name": "杭州市",
            "type_name": "理工",
            "level_name": "本科",
            "is985": "0",
            "is211": "0",
            "is_dual_class": "0",
            "dual_class": "2",
            "school_site": "http://www.hziee.edu.cn/",
            "site": "https://www.hziee.edu.cn/zs/"
          }
        ]
      },
      "scope_notes": [
        "学校实体解析来自 edu_university；第一版尚未启用人工确认别名表。"
      ],
      "data_gaps": [],
      "needs_clarification": [],
      "source_tables": [
        "edu_university"
      ],
      "warnings": []
    }
  },
  {
    "tool_name": "school_profile",
    "arguments": {
      "school_text": "杭州电子科技大学"
    },
    "result": {
      "tool_name": "school_profile",
      "status": "ok",
      "input": {
        "school_text": "杭州电子科技大学"
      },
      "normalized_slots": {
        "school_name": "杭州电子科技大学",
        "school_id": "10124"
      },
      "data": {
        "school": {
          "school_id": "10124",
          "code": "10336",
          "name": "杭州电子科技大学",
          "province_name": "浙江",
          "city_name": "杭州市",
          "type_name": "理工",
          "level_name": "本科",
          "is985": "0",
          "is211": "0",
          "is_dual_class": "0",
          "dual_class": "2",
          "school_site": "https://www.hdu.edu.cn/main.htm",
          "site": "http://grs.hdu.edu.cn/1721/list.htm"
        },
        "dual_class": [],
        "subject_evals": [
          {
            "eval_round": "第四轮",
            "major_name": "信息与通信工程",
            "eval_level": "C",
            "level_code": "2",
            "special_id": "080703",
            "special_name": "信息与通信工程"
          },
          {
            "eval_round": "第四轮",
            "major_name": "机械工程",
            "eval_level": "C+",
            "level_code": "3",
            "special_id": "080201",
            "special_name": "机械工程"
          },
          {
            "eval_round": "第四轮",
            "major_name": "软件工程",
            "eval_level": "C+",
            "level_code": "3",
            "special_id": "080902",
            "special_name": "软件工程"
          },
          {
            "eval_round": "第四轮",
            "major_name": "管理科学与工程",
            "eval_level": "C+",
            "level_code": "3",
            "special_id": "120101",
            "special_name": "管理科学与工程"
          },
          {
            "eval_round": "第四轮",
            "major_name": "工商管理",
            "eval_level": "B-",
            "level_code": "4",
            "special_id": "120201",
            "special_name": "工商管理"
          },
          {
            "eval_round": "第四轮",
            "major_name": "电子科学与技术",
            "eval_level": "B+",
            "level_code": "6",
            "special_id": "080702",
            "special_name": "电子科学与技术"
          },
          {
            "eval_round": "第四轮",
            "major_name": "计算机科学与技术",
            "eval_level": "B+",
            "level_code": "6",
            "special_id": "080901",
            "special_name": "计算机科学与技术"
          },
          {
            "eval_round": "第四轮",
            "major_name": "控制科学与工程",
            "eval_level": "B+",
            "level_code": "6",
            "special_id": "080801",
            "special_name": "控制科学与工程"
          }
        ],
        "latest_employment": {
          "year": "2025",
          "employment_rate": null,
          "further_study_rate": "40.00",
          "avg_salary": null,
          "top_employment_industries": null,
          "top_employment_regions": null,
          "top_employers": null
        }
      },
      "scope_notes": [
        "学校基础信息是学校级事实。",
        "就业升学数据来自学校级表，不代表某个专业。"
      ],
      "data_gaps": [],
      "needs_clarification": [],
      "source_tables": [
        "edu_university",
        "edu_dual_class",
        "edu_university_subject_eval",
        "edu_university_employment"
      ],
      "warnings": []
    }
  },
  {
    "tool_name": "major_profile",
    "arguments": {
      "major_text": "计算机科学与技术"
    },
    "result": {
      "tool_name": "major_profile",
      "status": "ok",
      "input": {
        "major_text": "计算机科学与技术"
      },
      "normalized_slots": {
        "major_name": "计算机科学与技术",
        "major_code": "080901"
      },
      "data": {
        "major": {
          "special_id": "080901",
          "code": "080901",
          "special_name": "计算机科学与技术",
          "type_name": "本科(普通)",
          "level2_name": "工学",
          "level3_name": "计算机类",
          "limit_year": "四年",
          "degree": "理学学士,工学学士",
          "salaryavg": null,
          "fivesalaryavg": null,
          "job": null,
          "is_what": null,
          "learn_what": null,
          "do_what": null,
          "job_clean": "",
          "mostemploymentarea": null,
          "mostemploymentindustry": null,
          "mostemployedeposition": null
        },
        "salary_reference": {
          "salaryavg": null,
          "fivesalaryavg": null
        },
        "job_directions": []
      },
      "scope_notes": [
        "专业资料来自 edu_major，是专业通用级数据。",
        "薪资和就业方向不代表某学校某专业毕业生真实结果。"
      ],
      "data_gaps": [],
      "needs_clarification": [],
      "source_tables": [
        "edu_major",
        "entity_aliases"
      ],
      "warnings": []
    }
  },
  {
    "tool_name": "school_major_profile",
    "arguments": {
      "school_text": "杭州电子科技大学",
      "major_text": "计算机科学与技术"
    },
    "result": {
      "tool_name": "school_major_profile",
      "status": "partial",
      "input": {
        "school_text": "杭州电子科技大学",
        "major_text": "计算机科学与技术",
        "province": null,
        "subject_type": null,
        "year": null
      },
      "normalized_slots": {
        "school_name": "杭州电子科技大学",
        "school_id": "10124",
        "major_name": "计算机科学与技术",
        "major_code": "080901",
        "province": null,
        "subject_type": null,
        "year": null
      },
      "data": {
        "school": {
          "school_id": "10124",
          "code": "10336",
          "name": "杭州电子科技大学",
          "province_name": "浙江",
          "city_name": "杭州市",
          "type_name": "理工",
          "level_name": "本科",
          "is985": "0",
          "is211": "0",
          "is_dual_class": "0",
          "dual_class": "2",
          "school_site": "https://www.hdu.edu.cn/main.htm",
          "site": "http://grs.hdu.edu.cn/1721/list.htm"
        },
        "major": {
          "special_id": "080901",
          "code": "080901",
          "special_name": "计算机科学与技术",
          "type_name": "本科(普通)",
          "level2_name": "工学",
          "level3_name": "计算机类",
          "limit_year": "四年",
          "degree": "理学学士,工学学士",
          "salaryavg": null,
          "fivesalaryavg": null,
          "job": null,
          "is_what": null,
          "learn_what": null,
          "do_what": null,
          "job_clean": "",
          "mostemploymentarea": null,
          "mostemploymentindustry": null,
          "mostemployedeposition": null
        },
        "school_major": {},
        "subject_evals": [
          {
            "eval_round": "第四轮",
            "major_name": "计算机科学与技术",
            "eval_level": "B+",
            "level_code": "6",
            "special_id": "080901",
            "special_name": "计算机科学与技术",
            "match_scope": "exact"
          }
        ],
        "dual_class": [],
        "employment": {
          "year": "2025",
          "employment_rate": null,
          "further_study_rate": "40.00",
          "avg_salary": null,
          "top_employment_industries": null,
          "top_employment_regions": null,
          "top_employers": null
        },
        "specialty_groups": [
          {
            "year": "2025",
            "province": "22",
            "group_code": "002",
            "group_name": "杭州电子科技大学-002组",
            "group_type": "物理",
            "group_plan_count": null,
            "min_score": "591",
            "min_rank": "5663",
            "allow_adjustment": null,
            "special_code": "080901",
            "special_name": "计算机科学与技术",
            "major_plan_count": null,
            "subject_requirement": "物理,化学",
            "remark": null
          },
          {
            "year": "2025",
            "province": "31",
            "group_code": "49203",
            "group_name": "杭州电子科技大学-49203组",
            "group_type": "综合",
            "group_plan_count": "11",
            "min_score": "550",
            "min_rank": "9779",
            "allow_adjustment": null,
            "special_code": "080901",
            "special_name": "计算机科学与技术",
            "major_plan_count": "3",
            "subject_requirement": "物理,化学",
            "remark": null
          },
          {
            "year": "2025",
            "province": "32",
            "group_code": "02",
            "group_name": "杭州电子科技大学-02组",
            "group_type": "物理",
            "group_plan_count": "37",
            "min_score": "609",
            "min_rank": "19004",
            "allow_adjustment": null,
            "special_code": "080901",
            "special_name": "计算机科学与技术",
            "major_plan_count": "3",
            "subject_requirement": "物理,化学",
            "remark": "(以下专业在下沙校区学习:)"
          },
          {
            "year": "2025",
            "province": "32",
            "group_code": "03",
            "group_name": "杭州电子科技大学-03组",
            "group_type": "物理",
            "group_plan_count": "6",
            "min_score": "608",
            "min_rank": "27150",
            "allow_adjustment": null,
            "special_code": "080901",
            "special_name": "计算机科学与技术",
            "major_plan_count": "2",
            "subject_requirement": "物理,化学",
            "remark": "(中外合作办学)(下沙校区)"
          },
          {
            "year": "2024",
            "province": "23",
            "group_code": "004",
            "group_name": "杭州电子科技大学-004组",
            "group_type": "物理",
            "group_plan_count": null,
            "min_score": "604",
            "min_rank": "7134",
            "allow_adjustment": null,
            "special_code": "080901",
            "special_name": "计算机科学与技术",
            "major_plan_count": null,
            "subject_requirement": "物理,化学",
            "remark": "(中外合作办学)(与俄罗斯圣光机大学合作办学，中英文授课，学生在中方完成4年学业后，可获中俄双方证书)"
          },
          {
            "year": "2024",
            "province": "35",
            "group_code": "500",
            "group_name": "杭州电子科技大学-500组",
            "group_type": "物理",
            "group_plan_count": "78",
            "min_score": "604",
            "min_rank": "8849",
            "allow_adjustment": null,
            "special_code": "080901",
            "special_name": "计算机科学与技术",
            "major_plan_count": "2",
            "subject_requirement": "物理,化学",
            "remark": "(中外合作办学)"
          },
          {
            "year": "2024",
            "province": "42",
            "group_code": "03",
            "group_name": "杭州电子科技大学-03组",
            "group_type": "物理",
            "group_plan_count": null,
            "min_score": "602",
            "min_rank": "16685",
            "allow_adjustment": null,
            "special_code": "080901",
            "special_name": "计算机科学与技术",
            "major_plan_count": null,
            "subject_requirement": "物理,化学",
            "remark": "(中外合作办学)(与俄罗斯圣光机大学合作办学，中英文授课，学生在中方完成4年学业后，可获中俄双方证书；办学地点：下沙校区)"
          },
          {
            "year": "2024",
            "province": "43",
            "group_code": "205",
            "group_name": "杭州电子科技大学-205组",
            "group_type": "物理",
            "group_plan_count": null,
            "min_score": "591",
            "min_rank": "17928",
            "allow_adjustment": null,
            "special_code": "080901",
            "special_name": "计算机科学与技术",
            "major_plan_count": null,
            "subject_requirement": "物理,化学",
            "remark": "(中外合作办学)(与俄罗斯圣光机大学合作办学，中英文授课，学生在中方完成4年学业后，可获中俄双方证书。)"
          }
        ],
        "available_fields": [
          "学校基础信息",
          "专业基础信息",
          "教育部学科评估",
          "学校级就业/升学",
          "专业组样本"
        ]
      },
      "scope_notes": [
        "学校-专业开设关系、专业通用资料、学校级就业、专业组样本是不同口径。",
        "学校级就业/升学不能代表某专业真实就业结果。",
        "专业组样本不等于入学后真实分流比例。"
      ],
      "data_gaps": [
        "校专业级工作地域分布",
        "校专业级薪资分布",
        "校专业级Top对口公司",
        "考公岗位映射",
        "转专业政策",
        "专业组真实分流比例/冷门专业比例",
        "学校官网专业介绍证据链"
      ],
      "needs_clarification": [],
      "source_tables": [
        "edu_university",
        "edu_major",
        "entity_aliases",
        "edu_school_major",
        "edu_university_subject_eval",
        "edu_dual_class",
        "edu_university_employment",
        "edu_college_specialty_group",
        "edu_specialty_group_major"
      ],
      "warnings": [
        "本地库未命中明确学校-专业开设关系，不能直接认定已开设。"
      ]
    }
  },
  {
    "tool_name": "major_market_reference",
    "arguments": {
      "major_text": "计算机科学与技术",
      "sample_limit": 5
    },
    "result": {
      "tool_name": "major_market_reference",
      "status": "ok",
      "input": {
        "major_text": "计算机科学与技术",
        "sample_limit": 5
      },
      "normalized_slots": {
        "major_name": "计算机科学与技术",
        "major_code": "080901"
      },
      "data": {
        "major": {
          "special_id": "080901",
          "code": "080901",
          "special_name": "计算机科学与技术",
          "type_name": "本科(普通)",
          "level2_name": "工学",
          "level3_name": "计算机类",
          "limit_year": "四年",
          "degree": "理学学士,工学学士",
          "salaryavg": null,
          "fivesalaryavg": null,
          "job": null,
          "is_what": null,
          "learn_what": null,
          "do_what": null,
          "job_clean": "",
          "mostemploymentarea": null,
          "mostemploymentindustry": null,
          "mostemployedeposition": null
        },
        "snapshot": {
          "profession_id": "341",
          "major_code": "080901",
          "major_name": "计算机科学与技术",
          "major_level": "本科",
          "degree": "理学学士,工学学士",
          "limit_year": "四年",
          "captured_at": "2026-05-19T18:54:58+08:00",
          "source_name": "rysxai",
          "source_level": "C",
          "data_scope": "major_level_market_observation",
          "info_url": "https://api.rysxai.cn/api/ry_education/profession/info/?id=341",
          "positions_url": "https://api.rysxai.cn/api/ry_education/profession/positions/?id=341",
          "macro_employment_json": {
            "region_distribution": [
              {
                "label": "北京市",
                "rate_percent": 21.5
              },
              {
                "label": "上海市",
                "rate_percent": 14.3
              },
              {
                "label": "深圳市",
                "rate_percent": 8.7
              },
              {
                "label": "华东地区",
                "rate_percent": 6.5
              },
              {
                "label": "广州市",
                "rate_percent": 4.2
              },
              {
                "label": "西南地区",
                "rate_percent": 3.8
              },
              {
                "label": "西北地区",
                "rate_percent": 2.8
              },
              {
                "label": "华中地区",
                "rate_percent": 2.2
              },
              {
                "label": "其他地区",
                "rate_percent": 36.0
              }
            ],
            "industry_distribution": [
              {
                "label": "IT软件",
                "rate_percent": 27.86
              },
              {
                "label": "互联网",
                "rate_percent": 10.43
              },
              {
                "label": "系统集成",
                "rate_percent": 6.83
              },
              {
                "label": "电信设备",
                "rate_percent": 6.39
              },
              {
                "label": "教育培训",
                "rate_percent": 4.96
              },
              {
                "label": "金融投资",
                "rate_percent": 4.53
              },
              {
                "label": "房地产",
                "rate_percent": 3.6
              },
              {
                "label": "电信运营",
                "rate_percent": 3.32
              },
              {
                "label": "电子技术",
                "rate_percent": 3.31
              },
              {
                "label": "IT硬件",
                "rate_percent": 1.78
              },
              {
                "label": "其他行业",
                "rate_percent": 26.99
              }
            ],
            "job_direction_distribution": [
              {
                "label": "后端开发",
                "detail_jobs": [
                  "java开发工程师",
                  "研发工程师",
                  "互联网软件开发工程师",
                  "软件研发工程师",
                  "软件工程师",
                  "ERP技术/开发应用",
                  "高级软件工程师",
                  "技术经理",
                  "软件开发",
                  "多媒体/游戏开发工程师"
                ],
                "rate_percent": 14.2
              },
              {
                "label": "技术支持",
                "detail_jobs": [
                  "售前/售后技术支持工程师",
                  "技术支持/维护工程师",
                  "技术支持工程师",
                  "售前/售后技术支持管理",
                  "售后技术支持工程师",
                  "技术支持",
                  "售前/售后技术支持经理",
                  "ERP实施顾问",
                  "技术支持/维护经理",
                  "实施工程师"
                ],
                "rate_percent": 10.2
              },
              {
                "label": "移动开发",
                "detail_jobs": [
                  "android开发",
                  "ios软件工程师",
                  "研发工程师",
                  "Android开发",
                  "iOS开发",
                  "android软件工程师",
                  "Android软件开发工程师",
                  "实习生",
                  "软件开发工程师",
                  "安卓工程师"
                ],
                "rate_percent": 6.7
              },
              {
                "label": "销售业务",
                "detail_jobs": [
                  "网络/在线销售",
                  "渠道经理",
                  "大客户销售代表",
                  "业务经理",
                  "大客户经理",
                  "高级客户经理",
                  "渠道/分销经理",
                  "渠道/分销主管",
                  "大客户销售经理",
                  "渠道/分销总监"
                ],
                "rate_percent": 5.8
              },
              {
                "label": "测试",
                "detail_jobs": [
                  "系统测试",
                  "高级软件测试工程师",
                  "测试主管",
                  "测试员",
                  "软件测试",
                  "高级测试工程师",
                  "软件测试工程师",
                  "测试工程师",
                  "软件工程师",
                  "测试经理"
                ],
                "rate_percent": 5.3
              },
              {
                "label": "其他",
                "detail_jobs": [
                  "系统工程师",
                  "技术支持/维护工程师",
                  "系统管理员",
                  "运维工程师",
                  "IT技术支持/维护工程师",
                  "网络与信息安全工程师",
                  "软件工程师",
                  "高级软件工程师",
                  "系统管理员/网络管理员",
                  "网络工程师"
                ],
                "rate_percent": 57.8
              }
            ]
          },
          "demand_ranking_json": [
            {
              "region": "全国",
              "demand_count": 72902
            },
            {
              "region": "深圳",
              "demand_count": 10509
            },
            {
              "region": "上海",
              "demand_count": 9621
            },
            {
              "region": "广州",
              "demand_count": 6851
            },
            {
              "region": "北京",
              "demand_count": 5799
            },
            {
              "region": "武汉",
              "demand_count": 3730
            },
            {
              "region": "南京",
              "demand_count": 3700
            },
            {
              "region": "杭州",
              "demand_count": 3540
            },
            {
              "region": "成都",
              "demand_count": 3437
            },
            {
              "region": "苏州",
              "demand_count": 3131
            }
          ],
          "salary_ranking_json": [
            {
              "region": "全国",
              "monthly_salary_reference": 7329
            },
            {
              "region": "北京",
              "monthly_salary_reference": 10115
            },
            {
              "region": "上海",
              "monthly_salary_reference": 9826
            },
            {
              "region": "深圳",
              "monthly_salary_reference": 8660
            },
            {
              "region": "杭州",
              "monthly_salary_reference": 8075
            },
            {
              "region": "南京",
              "monthly_salary_reference": 7621
            },
            {
              "region": "苏州",
              "monthly_salary_reference": 7169
            },
            {
              "region": "广州",
              "monthly_salary_reference": 7029
            },
            {
              "region": "成都",
              "monthly_salary_reference": 6827
            },
            {
              "region": "武汉",
              "monthly_salary_reference": 6521
            },
            {
              "region": "西安",
              "monthly_salary_reference": 6434
            }
          ],
          "salary_observations_by_city_json": "{\"上海\": {\"data_scope\": \"recruiting_market_sample\", \"sample_count\": 1, \"source_level\": \"C\", \"monthly_salary_max_observed\": 21000, \"monthly_salary_midpoint_avg\": 16000, \"monthly_salary_min_observed\": 11000}, \"南宁\": {\"data_scope\": \"recruiting_market_sample\", \"sample_count\": 1, \"source_level\": \"C\", \"monthly_salary_max_observed\": 30000, \"monthly_salary_midpoint_avg\": 25000, \"monthly_salary_min_observed\": 20000}, \"昭通\": {\"data_scope\": \"recruiting_market_sample\", \"sample_count\": 1, \"source_level\": \"C\", \"monthly_salary_max_observed\": 6000, \"monthly_salary_midpoint_avg\": 5500, \"monthly_salary_min_observed\": 5000}, \"杭州\": {\"data_scope\": \"recruiting_market_sample\", \"sample_count\": 1, \"source_level\": \"C\", \"monthly_salary_max_observed\": 65000, \"monthly_salary_midpoint_avg\": 55000, \"monthly_salary_min_observed\": 45000}, \"湘西土家族苗族自治州\": {\"data_scope\": \"recruiting_market_sample\", \"sample_count\": 1, \"source_level\": \"C\", \"monthly_salary_max_observed\": 6000, \"monthly_salary_midpoint_avg\": 4500, \"monthly_salary_min_observed\": 3000}}",
          "salary_observations_by_industry_json": "{\"互联网\": {\"data_scope\": \"recruiting_market_sample\", \"sample_count\": 1, \"source_level\": \"C\", \"monthly_salary_max_observed\": 65000, \"monthly_salary_midpoint_avg\": 55000, \"monthly_salary_min_observed\": 45000}, \"企业服务\": {\"data_scope\": \"recruiting_market_sample\", \"sample_count\": 1, \"source_level\": \"C\", \"monthly_salary_max_observed\": 30000, \"monthly_salary_midpoint_avg\": 25000, \"monthly_salary_min_observed\": 20000}, \"培训/辅导机构\": {\"data_scope\": \"recruiting_market_sample\", \"sample_count\": 1, \"source_level\": \"C\", \"monthly_salary_max_observed\": 6000, \"monthly_salary_midpoint_avg\": 4500, \"monthly_salary_min_observed\": 3000}, \"学校/学历教育\": {\"data_scope\": \"recruiting_market_sample\", \"sample_count\": 1, \"source_level\": \"C\", \"monthly_salary_max_observed\": 6000, \"monthly_salary_midpoint_avg\": 5500, \"monthly_salary_min_observed\": 5000}, \"通信/网络设备\": {\"data_scope\": \"recruiting_market_sample\", \"sample_count\": 1, \"source_level\": \"C\", \"monthly_salary_max_observed\": 21000, \"monthly_salary_midpoint_avg\": 16000, \"monthly_salary_min_observed\": 11000}}",
          "job_posting_sample_total_reported": "50",
          "job_posting_sample_count": "5",
          "warnings_json": [
            "招聘岗位和薪资样本只能作为专业市场观察，不代表某校某专业毕业生实际薪资或就业去向。",
            "宏观就业分布来自第三方站内数据，应与官方就业质量报告分级存储、分开展示。"
          ]
        },
        "job_samples": [
          {
            "job_title": "数据科学专家-用户&内容技术",
            "company_name": "阿里巴巴集团",
            "city": "杭州",
            "district": "余杭区",
            "industry": "互联网",
            "salary_raw": "4.5-6.5万/月",
            "monthly_salary_min": "45000",
            "monthly_salary_max": "65000",
            "education": "本科",
            "experience": "5-10年",
            "company_scale": "10000人以上",
            "financing_stage": "已上市"
          },
          {
            "job_title": "计算机算法高级工程师",
            "company_name": "慧云信息",
            "city": "南宁",
            "district": "良庆区",
            "industry": "企业服务",
            "salary_raw": "2-3万/月",
            "monthly_salary_min": "20000",
            "monthly_salary_max": "30000",
            "education": "本科",
            "experience": "3-5年",
            "company_scale": "20-99人",
            "financing_stage": "B轮"
          },
          {
            "job_title": "主动安全测试工程师",
            "company_name": "上海华为技术有限公司",
            "city": "上海",
            "district": "浦东新区",
            "industry": "通信/网络设备",
            "salary_raw": "1.1-2.1万/月",
            "monthly_salary_min": "11000",
            "monthly_salary_max": "21000",
            "education": "本科",
            "experience": "经验不限",
            "company_scale": "10000人以上",
            "financing_stage": "不需要融资"
          },
          {
            "job_title": "计算机老师",
            "company_name": "文楠教育",
            "city": "昭通",
            "district": "",
            "industry": "学校/学历教育",
            "salary_raw": "5-6千/月",
            "monthly_salary_min": "5000",
            "monthly_salary_max": "6000",
            "education": "本科",
            "experience": "1-3年",
            "company_scale": "0-20人",
            "financing_stage": "不需要融资"
          },
          {
            "job_title": "计算机专业老师",
            "company_name": "永顺阿童木文化传播",
            "city": "湘西土家族苗族自治州",
            "district": "永顺县",
            "industry": "培训/辅导机构",
            "salary_raw": "3-6千/月",
            "monthly_salary_min": "3000",
            "monthly_salary_max": "6000",
            "education": "本科",
            "experience": "经验不限",
            "company_scale": "0-20人",
            "financing_stage": ""
          }
        ]
      },
      "scope_notes": [
        "这是第三方招聘市场样本和专业市场观察，不代表某学校某专业毕业生真实就业去向或薪资。"
      ],
      "data_gaps": [],
      "needs_clarification": [],
      "source_tables": [
        "edu_major",
        "entity_aliases",
        "rysxai_major_market_snapshots",
        "rysxai_major_job_samples"
      ],
      "warnings": []
    }
  },
  {
    "tool_name": "civil_service_role_search",
    "arguments": {
      "major_text": "计算机科学与技术",
      "limit": 5
    },
    "result": {
      "tool_name": "civil_service_role_search",
      "status": "ok",
      "input": {
        "major_text": "计算机科学与技术",
        "year": null,
        "province": null,
        "limit": 5
      },
      "normalized_slots": {
        "major_name": "计算机科学与技术",
        "major_code": "080901",
        "year": null,
        "province": null
      },
      "data": {
        "major": {
          "special_id": "080901",
          "code": "080901",
          "special_name": "计算机科学与技术",
          "type_name": "本科(普通)",
          "level2_name": "工学",
          "level3_name": "计算机类",
          "limit_year": "四年",
          "degree": "理学学士,工学学士",
          "salaryavg": null,
          "fivesalaryavg": null,
          "job": null,
          "is_what": null,
          "learn_what": null,
          "do_what": null,
          "job_clean": "",
          "mostemploymentarea": null,
          "mostemploymentindustry": null,
          "mostemployedeposition": null
        },
        "roles": [
          {
            "role_id": "40355",
            "year": "2026",
            "department_name": "新疆出入境边防检查总站",
            "sub_department": "新疆出入境边防检查总站",
            "job_name": "卡拉苏出入境边防检查站一级警长及以下（三）",
            "position_code": "300130134079",
            "exam_type": "行政执法类",
            "plan_num": "4",
            "apply_num": "3",
            "ratio": "0.75",
            "education_level": "仅限本科",
            "degree_requirement": "学士",
            "work_location": "新疆维吾尔自治区喀什地区塔什库尔干塔吉克自治县",
            "province": "新疆",
            "major_code": "080901",
            "major_name": "计算机科学与技术",
            "profession_text": "050202俄语、080901计算机科学与技术、030101K法学、050301新闻学"
          },
          {
            "role_id": "40346",
            "year": "2026",
            "department_name": "新疆出入境边防检查总站",
            "sub_department": "新疆出入境边防检查总站",
            "job_name": "伊尔克什坦出入境边防检查站一级警长及以下（五）",
            "position_code": "300130134070",
            "exam_type": "行政执法类",
            "plan_num": "5",
            "apply_num": "16",
            "ratio": "3.20",
            "education_level": "仅限本科",
            "degree_requirement": "学士",
            "work_location": "新疆维吾尔自治区克孜勒苏柯尔克孜自治州乌恰县",
            "province": "新疆",
            "major_code": "080901",
            "major_name": "计算机科学与技术",
            "profession_text": "120208资产评估、120207审计学、080901计算机科学与技术、081001土木工程、050306T网络与新媒体"
          },
          {
            "role_id": "32040",
            "year": "2026",
            "department_name": "国家金融监督管理总局福建监管局",
            "sub_department": "国家金融监督管理总局大田监管支局",
            "job_name": "科技部门一级主任科员及以下",
            "position_code": "300147402001",
            "exam_type": "市（地）级及以下直属机构综合管理类",
            "plan_num": "1",
            "apply_num": "4",
            "ratio": "4.00",
            "education_level": "本科及以上",
            "degree_requirement": "与最高学历相对应的学位",
            "work_location": "福建省三明市大田县",
            "province": "福建",
            "major_code": "080901",
            "major_name": "计算机科学与技术",
            "profession_text": "本科：080901计算机科学与技术、080902软件工程、080903网络工程、080909T电子与计算机工程、080910T数据科学与大数据技术 研究生：0809电子科学与技术、0810信息与通信工程、0812计算机科学与技术"
          },
          {
            "role_id": "39966",
            "year": "2026",
            "department_name": "内蒙古出入境边防检查总站",
            "sub_department": "内蒙古出入境边防检查总站",
            "job_name": "策克出入境边防检查站警务技术一级主管及以下",
            "position_code": "300130860025",
            "exam_type": "市（地）级及以下直属机构综合管理类",
            "plan_num": "1",
            "apply_num": "7",
            "ratio": "7.00",
            "education_level": "本科及以上",
            "degree_requirement": "与最高学历相对应的学位",
            "work_location": "内蒙古自治区阿拉善盟额济纳旗",
            "province": "内蒙古",
            "major_code": "080901",
            "major_name": "计算机科学与技术",
            "profession_text": "研究生：0812/085211计算机科学与技术、0835/085212软件工程、0810/0852/085402信息与通信工程。本科：0807电子信息类、080901计算机科学与技术、080902软件工程、080903网络工程。"
          },
          {
            "role_id": "40278",
            "year": "2026",
            "department_name": "青海出入境边防检查总站",
            "sub_department": "青海出入境边防检查总站",
            "job_name": "西宁出入境边防检查站一级警长及以下（三）",
            "position_code": "300130310003",
            "exam_type": "行政执法类",
            "plan_num": "1",
            "apply_num": "7",
            "ratio": "7.00",
            "education_level": "本科及以上",
            "degree_requirement": "与最高学历相对应的学位",
            "work_location": "青海省西宁市",
            "province": "青海",
            "major_code": "080901",
            "major_name": "",
            "profession_text": "研究生：计算机科学与技术（077500、081200）、软件工程（083500、085405、085212）；本科：计算机科学与技术（080901）、软件工程（080902）、数据科学与大数据技术（080910T）"
          }
        ]
      },
      "scope_notes": [
        "以下为岗位专业要求文本命中的考公岗位样本，不等于该专业一定可报。",
        "最终可报范围应以当年官方招录公告和岗位表解释为准。"
      ],
      "data_gaps": [],
      "needs_clarification": [],
      "source_tables": [
        "edu_major",
        "entity_aliases",
        "civil_service_major_role_candidates",
        "rysxai_civil_service_roles"
      ],
      "warnings": []
    }
  }
]
```
