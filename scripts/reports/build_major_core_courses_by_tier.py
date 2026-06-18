"""Build major core-course estimates with university-tier examples.

Inputs:
- reports/remote_db_university_tiers/remote_edu_university_three_tiers_20260614.csv
- reports/remote_db_current_majors/remote_edu_major_majors_20260614.csv
- data/processed/rysxai_major_intros/major_introductions_full_20260611_intro.jsonl
- tmp/edu_major_course_dump.tsv
- tmp/edu_school_major_dump.tsv
"""

from __future__ import annotations

import csv
import json
import re
from collections import OrderedDict, defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
TIER_CSV = ROOT / "reports/remote_db_university_tiers/remote_edu_university_three_tiers_20260614.csv"
TIER_SUMMARY = ROOT / "reports/remote_db_university_tiers/remote_edu_university_three_tiers_summary_20260614.csv"
CATALOG_CSV = ROOT / "reports/remote_db_current_majors/remote_edu_major_majors_20260614.csv"
INTRO_JSONL = ROOT / "data/processed/rysxai_major_intros/major_introductions_full_20260611_intro.jsonl"
LOCAL_MAJOR_TSV = ROOT / "tmp/edu_major_course_dump.tsv"
SCHOOL_MAJOR_TSV = ROOT / "tmp/edu_school_major_dump.tsv"
DEPARTMENT_MAJOR_TSV = ROOT / "tmp/edu_department_major_dump.tsv"
OUT_DIR = ROOT / "reports/major_core_courses_by_tier"
OUT_CSV = OUT_DIR / "major_core_courses_by_tier_20260614.csv"
OUT_MD = OUT_DIR / "major_core_courses_by_tier_sample_20260614.md"

SUFFIX_RE = re.compile(r"(TK|K|T)$", re.I)
COURSE_SPLIT_RE = re.compile(r"[、,，/；;]|和|与")
GENERIC_NOISE = {
    "课程",
    "课程体系",
    "专业基础类课程",
    "专业核心课",
    "专业基础课程",
    "专业核心课程",
    "实践课程",
    "选修课程",
    "介绍",
    "类别介绍",
    "专业介绍",
    "课程介绍",
    "—课程介绍",
}
BAD_PREFIXES = (
    "课程名称",
    "主要课程",
    "核心课程",
    "专业核心课程",
    "基础课程",
    "专业基础课程",
    "是",
    "学",
    "帮助",
    "培养",
    "包括",
    "涵盖",
    "聚焦",
    "围绕",
    "用于",
    "通过",
)


TEMPLATES: OrderedDict[str, list[str]] = OrderedDict(
    [
        ("哲学类", ["哲学导论", "逻辑学", "马克思主义哲学", "中国哲学史", "西方哲学史", "伦理学", "宗教学", "哲学原著选读"]),
        ("经济学类", ["微观经济学", "宏观经济学", "政治经济学", "计量经济学", "统计学", "财政学", "金融学", "发展经济学"]),
        ("财政学类", ["财政学", "税收学", "政府预算", "公共经济学", "计量经济学", "会计学", "税收筹划", "财政政策分析"]),
        ("金融学类", ["金融学", "公司金融", "投资学", "金融市场学", "商业银行经营管理", "金融工程", "计量经济学", "风险管理"]),
        ("经济与贸易类", ["国际贸易学", "国际金融", "国际商法", "国际结算", "商务英语", "跨境电商", "计量经济学", "外贸实务"]),
        ("法学类", ["法理学", "宪法学", "民法", "刑法", "行政法与行政诉讼法", "商法", "经济法", "民事诉讼法"]),
        ("政治学类", ["政治学原理", "比较政治制度", "国际政治学", "公共政策分析", "行政学", "政治思想史", "社会调查方法", "当代中国政治制度"]),
        ("社会学类", ["社会学概论", "社会调查研究方法", "社会统计学", "社会心理学", "社会工作概论", "社区治理", "社会政策", "质性研究方法"]),
        ("教育学类", ["教育学原理", "普通心理学", "教育心理学", "课程与教学论", "教育研究方法", "教育测量与评价", "班级管理", "教师职业技能"]),
        ("体育学类", ["运动解剖学", "运动生理学", "体育概论", "体育心理学", "运动训练学", "学校体育学", "体育统计学", "专项运动训练"]),
        ("中国语言文学类", ["现代汉语", "古代汉语", "中国古代文学", "中国现当代文学", "外国文学", "文学概论", "写作", "语言学概论"]),
        ("外国语言文学类", ["综合外语", "高级外语", "外语听说", "外语写作", "语言学概论", "翻译理论与实践", "外国文学", "跨文化交际"]),
        ("新闻传播学类", ["新闻学概论", "传播学概论", "新闻采访与写作", "新闻编辑", "媒体经营管理", "新媒体传播", "舆论学", "数据新闻"]),
        ("历史学类", ["中国古代史", "中国近现代史", "世界古代史", "世界近现代史", "史学概论", "史料学", "历史文献学", "考古学概论"]),
        ("数学类", ["数学分析", "高等代数", "解析几何", "概率论", "数理统计", "常微分方程", "复变函数", "数学建模"]),
        ("物理学类", ["力学", "热学", "电磁学", "光学", "原子物理", "理论力学", "量子力学", "普通物理实验"]),
        ("化学类", ["无机化学", "有机化学", "分析化学", "物理化学", "结构化学", "化工原理", "仪器分析", "综合化学实验"]),
        ("生物科学类", ["普通生物学", "植物学", "动物学", "微生物学", "生物化学", "遗传学", "细胞生物学", "分子生物学"]),
        ("心理学类", ["普通心理学", "发展心理学", "实验心理学", "心理统计", "心理测量", "认知心理学", "人格心理学", "心理咨询基础"]),
        ("统计学类", ["数学分析", "高等代数", "概率论", "数理统计", "回归分析", "多元统计分析", "时间序列分析", "统计软件"]),
        ("机械类", ["工程制图", "理论力学", "材料力学", "机械原理", "机械设计", "机械制造基础", "控制工程基础", "CAD/CAM"]),
        ("材料类", ["材料科学基础", "材料物理化学", "材料力学性能", "材料现代分析方法", "金属材料学", "高分子材料", "材料成型原理", "材料工艺实验"]),
        ("能源动力类", ["工程热力学", "传热学", "流体力学", "燃烧学", "热工测试技术", "动力机械", "能源系统分析", "制冷与热泵"]),
        ("电气类", ["电路", "模拟电子技术", "数字电子技术", "电机学", "电力电子技术", "自动控制原理", "电力系统分析", "继电保护"]),
        ("电子信息类", ["电路分析", "模拟电子技术", "数字电子技术", "信号与系统", "通信原理", "电磁场与电磁波", "嵌入式系统", "数字信号处理"]),
        ("自动化类", ["电路", "模拟电子技术", "数字电子技术", "自动控制原理", "现代控制理论", "过程控制", "运动控制", "PLC与工业控制"]),
        ("计算机类", ["程序设计", "离散数学", "数据结构", "计算机组成原理", "操作系统", "计算机网络", "数据库系统", "软件工程", "算法设计与分析"]),
        ("土木类", ["理论力学", "材料力学", "结构力学", "土力学", "混凝土结构", "钢结构", "工程测量", "施工组织"]),
        ("水利类", ["水力学", "工程水文学", "水工建筑物", "水资源规划", "河流动力学", "水利工程施工", "工程测量", "水环境保护"]),
        ("测绘类", ["测量学", "误差理论与测量平差", "GNSS原理", "摄影测量学", "遥感原理", "地理信息系统", "工程测量", "空间数据库"]),
        ("化工与制药类", ["无机化学", "有机化学", "物理化学", "化工原理", "化学反应工程", "化工热力学", "分离工程", "化工设计"]),
        ("交通运输类", ["交通运输工程导论", "运筹学", "交通规划", "交通控制与管理", "运输组织学", "物流系统工程", "交通安全", "智能交通系统"]),
        ("航空航天类", ["理论力学", "材料力学", "空气动力学", "飞行器结构", "飞行器设计", "推进原理", "自动控制原理", "航天器动力学"]),
        ("环境科学与工程类", ["环境学导论", "环境化学", "环境监测", "环境工程微生物学", "水污染控制工程", "大气污染控制工程", "固体废物处理", "环境影响评价"]),
        ("食品科学与工程类", ["食品化学", "食品微生物学", "食品工程原理", "食品工艺学", "食品营养学", "食品安全学", "食品分析", "食品机械"]),
        ("建筑类", ["建筑设计基础", "建筑设计", "建筑历史", "建筑构造", "建筑物理", "城市规划原理", "建筑结构", "场地设计"]),
        ("植物生产类", ["植物学", "植物生理学", "遗传学", "土壤肥料学", "作物栽培学", "植物保护学", "种子学", "农业生态学"]),
        ("动物生产类", ["动物解剖生理学", "动物营养学", "动物遗传育种", "动物繁殖学", "饲料学", "畜牧生产学", "动物环境卫生", "牧场管理"]),
        ("动物医学类", ["动物解剖学", "动物生理学", "兽医病理学", "兽医药理学", "兽医微生物学", "兽医临床诊断学", "内科学", "外科学"]),
        ("临床医学类", ["人体解剖学", "生理学", "病理学", "药理学", "诊断学", "内科学", "外科学", "妇产科学", "儿科学"]),
        ("口腔医学类", ["口腔解剖生理学", "口腔组织病理学", "口腔材料学", "口腔内科学", "口腔颌面外科学", "口腔修复学", "口腔正畸学", "口腔预防医学"]),
        ("公共卫生与预防医学类", ["流行病学", "卫生统计学", "环境卫生学", "职业卫生与职业医学", "营养与食品卫生学", "卫生毒理学", "社会医学", "公共卫生实践"]),
        ("中医学类", ["中医基础理论", "中医诊断学", "中药学", "方剂学", "中医内科学", "针灸学", "黄帝内经选读", "伤寒论"]),
        ("药学类", ["药物化学", "药剂学", "药理学", "药物分析", "生药学", "药事管理学", "临床药学", "药品质量控制"]),
        ("医学技术类", ["人体解剖生理学", "临床医学概论", "医学检验技术", "医学影像技术", "病理检验技术", "仪器分析", "质量控制", "临床实训"]),
        ("护理学类", ["基础护理学", "健康评估", "内科护理学", "外科护理学", "妇产科护理学", "儿科护理学", "急救护理学", "护理伦理学"]),
        ("工商管理类", ["管理学", "经济学", "会计学", "财务管理", "市场营销", "组织行为学", "运营管理", "战略管理"]),
        ("公共管理类", ["管理学", "公共管理学", "公共政策分析", "行政法", "公共经济学", "社会调查方法", "电子政务", "绩效管理"]),
        ("物流管理与工程类", ["管理学", "运筹学", "物流学", "供应链管理", "仓储与配送管理", "运输管理", "物流信息系统", "采购管理"]),
        ("电子商务类", ["电子商务概论", "网络营销", "电子商务运营", "数据库基础", "网页设计", "商务数据分析", "供应链管理", "跨境电商"]),
        ("旅游管理类", ["旅游学概论", "旅游经济学", "旅游市场营销", "旅游资源规划", "酒店管理", "旅行社经营管理", "旅游消费者行为", "服务管理"]),
        ("设计学类", ["设计素描", "设计色彩", "设计构成", "设计史", "图形创意", "计算机辅助设计", "用户研究", "专题设计"]),
        ("财务会计类", ["基础会计", "财务会计", "成本会计", "管理会计", "税法", "财务管理", "审计基础", "会计信息系统"]),
        ("建设工程管理类", ["建筑识图", "建筑材料", "工程测量", "建筑施工技术", "工程计量与计价", "工程项目管理", "工程招投标", "BIM应用"]),
        ("土建施工类", ["建筑识图", "建筑材料", "工程测量", "建筑力学", "建筑施工技术", "施工组织", "质量与安全管理", "建筑工程计量"]),
        ("护理类", ["基础护理技术", "健康评估", "内科护理", "外科护理", "妇产科护理", "儿科护理", "急救护理", "护理综合实训"]),
        ("机电设备类", ["机械制图", "机械基础", "电工电子技术", "液压与气动", "PLC应用", "设备安装与维护", "数控技术", "综合实训"]),
        ("道路运输类", ["汽车构造", "汽车电气设备", "汽车检测与诊断", "道路运输组织", "交通安全", "汽车维修技术", "物流运输管理", "岗位实训"]),
        ("铁道运输类", ["铁道概论", "铁路行车组织", "铁路客运组织", "列车运行控制", "铁路信号基础", "铁路安全管理", "车站作业", "岗位实训"]),
        ("航空运输类", ["民航概论", "航空服务礼仪", "民航安全管理", "客舱服务", "航空运输地理", "民航法规", "应急处置", "岗位实训"]),
    ]
)

LEVEL2_TEMPLATES = {
    "哲学": TEMPLATES["哲学类"],
    "经济学": TEMPLATES["经济学类"],
    "法学": TEMPLATES["法学类"],
    "教育学": TEMPLATES["教育学类"],
    "文学": TEMPLATES["中国语言文学类"],
    "历史学": TEMPLATES["历史学类"],
    "理学": ["高等数学", "线性代数", "概率论与数理统计", "专业导论", "专业核心理论", "实验方法", "数据分析", "科研训练"],
    "工学": ["高等数学", "大学物理", "工程制图", "电工电子技术", "工程力学", "专业核心原理", "工程实验", "课程设计"],
    "农学": TEMPLATES["植物生产类"],
    "医学": TEMPLATES["临床医学类"],
    "管理学": TEMPLATES["工商管理类"],
    "艺术学": TEMPLATES["设计学类"],
}
ADVANCED_HINTS = {
    "理学": "数学建模、科研方法、前沿专题、文献研读",
    "工学": "高阶数学/物理、系统设计、科研训练、交叉前沿专题",
    "医学": "循证医学、临床科研、规范化临床技能、病例讨论",
    "农学": "实验设计、育种/生态前沿、田间试验、数据分析",
    "经济学": "高级微宏观、计量建模、政策评估、数据实证",
    "管理学": "战略分析、商业数据分析、案例研究、组织/运营实证",
    "法学": "法学方法论、部门法专题、案例研判、比较法",
    "文学": "原典研读、语言/文本分析、学术写作、跨文化专题",
    "艺术学": "创作研究、设计方法论、作品集/展演、批评理论",
}
PRACTICE_HINTS = {
    "理学": "实验操作、数据处理、应用软件、毕业实训",
    "工学": "工具链、工艺流程、项目实训、岗位规范",
    "医学": "基础技能、临床见习、护理/检验/影像操作规范、资格考试衔接",
    "农学": "生产实训、田间/养殖操作、病虫害识别、经营管理",
    "经济学": "Excel/统计软件、业务流程、案例实训、岗位证书",
    "管理学": "业务系统、流程操作、项目案例、职业证书",
    "法学": "法律文书、模拟法庭、基层治理案例、实务流程",
    "文学": "写作、编辑、新媒体工具、教育/传播实训",
    "艺术学": "软件工具、项目制作、作品集、岗位实训",
}
SAMPLE_MAJOR_NAMES = [
    "哲学",
    "经济学",
    "金融学",
    "法学",
    "汉语言文学",
    "英语",
    "数学与应用数学",
    "计算机科学与技术",
    "软件工程",
    "人工智能",
    "电子信息工程",
    "电气工程及其自动化",
    "机械工程",
    "土木工程",
    "临床医学",
    "口腔医学",
    "护理学",
    "药学",
    "会计学",
    "电子商务",
    "大数据与会计",
    "护理",
    "机电一体化技术",
    "工程造价",
    "计算机应用技术",
    "数字媒体技术",
]


def norm_code(value: Any) -> str:
    text = str(value or "").strip().upper()
    if not text or text == "NULL":
        return ""
    return SUFFIX_RE.sub("", text)


def clean_text(value: Any) -> str:
    if value is None:
        return ""
    text = str(value).replace("\r", "\n").strip()
    if text == "NULL":
        return ""
    return re.sub(r"\n{3,}", "\n\n", text)


def dedupe_keep_order(items: list[str]) -> list[str]:
    seen: set[str] = set()
    output: list[str] = []
    for item in items:
        item = re.sub(r"\s+", "", str(item or "").strip(" ：:；;，,。.-"))
        if not item or item in seen or item in GENERIC_NOISE:
            continue
        if item.isdigit():
            continue
        if any(token in item for token in ("帮学生", "帮你", "写代码", "听懂")):
            continue
        if len(item) < 2 or len(item) > 18:
            continue
        if any(item.startswith(prefix) for prefix in BAD_PREFIXES):
            continue
        if re.search(r"[()（）？?]", item):
            continue
        seen.add(item)
        output.append(item)
    return output


def extract_courses(text: str) -> list[str]:
    text = clean_text(text)
    if not text:
        return []
    candidates: list[str] = []
    for raw in text.split("\n"):
        line = raw.strip()
        if not line:
            continue
        line = re.sub(r"^#{1,6}\s*", "", line)
        line = re.sub(r"^[-*•]\s*", "", line)
        line = re.sub(r"^\d+[\.\u3001)]\s*", "", line)
        line = re.sub(r"\*\*|`", "", line).strip()
        if not line or line[:2] in {"一、", "二、", "三、", "四、", "五、"}:
            continue
        if "课程名称" in line:
            value = re.sub(r"^.*?课程名称[：:]", "", line)
            candidates.append(re.split(r"[。；;，,]", value)[0])
            continue
        if "：" in line or ":" in line:
            head = re.split(r"[：:]", line, maxsplit=1)[0]
            head = re.sub(r"^(课程|核心|基础|专业|主要)", "", head).strip()
            if "课程" not in head or len(head) <= 12:
                candidates.append(head)
            if len(head) > 8 and any(token in head for token in ["包括", "涵盖", "主要"]):
                tail = re.split(r"[：:]", line, maxsplit=1)[1]
                candidates.extend(COURSE_SPLIT_RE.split(tail))
            continue
        if any(token in line for token in ["包括", "主要有", "核心课程有"]) and len(line) < 80:
            line = re.sub(r"^.*?(包括|主要有|核心课程有)", "", line)
            candidates.extend(COURSE_SPLIT_RE.split(line))
    return dedupe_keep_order(candidates)


def pick_template(level3: str, level2: str, name: str, is_vocational: bool) -> list[str]:
    if "大数据与会计" in name:
        return ["基础会计", "财务会计", "成本会计", "管理会计", "税法", "财务管理", "会计信息系统", "商务数据分析", "Python基础", "财务共享实训"]
    if "大数据与财务管理" in name:
        return ["基础会计", "财务管理", "管理会计", "税法", "财务报表分析", "预算管理", "商务数据分析", "Python基础", "财务共享实训"]
    if "人工智能" in name:
        return ["程序设计", "离散数学", "数据结构", "机器学习", "深度学习", "计算机视觉", "自然语言处理", "智能系统实践"]
    if "数据科学" in name or "大数据" in name:
        return ["程序设计", "数据结构", "数据库系统", "概率论与数理统计", "机器学习", "数据挖掘", "大数据平台技术", "数据可视化"]
    if "网络空间安全" in name or "信息安全" in name:
        return ["程序设计", "数据结构", "计算机网络", "操作系统", "密码学", "网络安全", "系统安全", "安全攻防实践"]
    if "软件工程" in name:
        return ["程序设计", "离散数学", "数据结构", "操作系统", "数据库系统", "软件工程", "软件测试", "项目管理"]
    if "会计" in name:
        return TEMPLATES["财务会计类"]
    if "护理" in name:
        return TEMPLATES["护理类"] if is_vocational else TEMPLATES["护理学类"]
    if "临床医学" in name:
        return TEMPLATES["临床医学类"]
    if "口腔医学" in name:
        return TEMPLATES["口腔医学类"]
    if "电子商务" in name:
        return TEMPLATES["电子商务类"]
    if "工程造价" in name:
        return ["建筑识图", "建筑材料", "工程测量", "建筑施工技术", "工程计量与计价", "安装工程计量", "工程招投标", "BIM造价应用"]
    if "机电一体化" in name:
        return ["机械制图", "机械基础", "电工电子技术", "液压与气动", "PLC控制技术", "传感器技术", "工业机器人应用", "综合实训"]
    if level3 in TEMPLATES:
        return TEMPLATES[level3]
    for key, value in TEMPLATES.items():
        if key and key in level3:
            return value
    if level2 in LEVEL2_TEMPLATES:
        return LEVEL2_TEMPLATES[level2]
    if is_vocational:
        return ["专业导论", "岗位基础技能", "专业核心技术", "设备/软件操作", "项目实训", "职业规范", "综合实训", "顶岗实习"]
    return ["专业导论", "学科基础课程", "专业核心理论", "专业方法与工具", "实验/实践课程", "方向模块课程", "课程设计", "毕业论文/设计"]


def tier_focus(tier: str, examples: list[str], level2: str) -> str:
    example_text = "、".join(examples[:5]) if examples else "库内未命中该层次开设样例"
    if tier == "1":
        hint = ADVANCED_HINTS.get(level2 or "", "理论深度、科研训练、交叉前沿、学术写作")
        return f"头部/强研究型：核心课不一定换名称，但会加深数学/理论和研究训练，重点看{hint}；样例：{example_text}"
    if tier == "2":
        return f"区域重点/特色优势：核心课保持完整，通常叠加地方产业、行业场景、实验项目和专业方向模块；样例：{example_text}"
    hint = PRACTICE_HINTS.get(level2 or "", "岗位技能、项目实训、证书衔接、综合实践")
    return f"普通应用/职业供给：更强调{hint}，课程呈现更实训化、工具化；样例：{example_text}"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def read_tsv(path: Path) -> list[dict[str, str]]:
    for encoding in ("utf-8-sig", "utf-16", "gb18030"):
        try:
            with path.open("r", encoding=encoding, newline="") as handle:
                return list(csv.DictReader(handle, delimiter="\t"))
        except UnicodeError:
            continue
    raise UnicodeError(f"Cannot decode {path}")


def load_intro_maps() -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
    by_code: dict[str, dict[str, Any]] = {}
    by_norm_code: dict[str, dict[str, Any]] = {}
    by_name: dict[str, dict[str, Any]] = {}
    with INTRO_JSONL.open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            snapshot = json.loads(line)
            profession = snapshot.get("profession") or {}
            code = str(profession.get("code") or "").strip().upper()
            name = str(profession.get("name") or "").strip()
            if code:
                by_code[code] = snapshot
                by_norm_code[norm_code(code)] = snapshot
            if name:
                by_name[name] = snapshot
    return by_code, by_norm_code, by_name


def sort_school_key(item: tuple[str, dict[str, str]]) -> tuple[int, int, int, str]:
    name, info = item
    rank_raw = info.get("ruanke_rank") or info.get("ranking") or "999999"
    try:
        rank = int(float(rank_raw))
    except ValueError:
        rank = 999999
    elite = -(int(info.get("is985") == "1") * 3 + int(info.get("is211") == "1") * 2 + int(info.get("is_dual_class") == "1"))
    public = 0 if info.get("school_nature_name") == "公办" else 1
    return elite, rank, public, name


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    catalog_rows = read_csv(CATALOG_CSV)
    tier_rows = read_csv(TIER_CSV)
    tier_summary_rows = read_csv(TIER_SUMMARY)
    local_major_rows = read_tsv(LOCAL_MAJOR_TSV)
    relation_tsv = DEPARTMENT_MAJOR_TSV if DEPARTMENT_MAJOR_TSV.exists() and DEPARTMENT_MAJOR_TSV.stat().st_size > 0 else SCHOOL_MAJOR_TSV
    school_major_rows = read_tsv(relation_tsv)
    intro_by_code, intro_by_norm_code, intro_by_name = load_intro_maps()

    tier_by_school_id: dict[str, dict[str, str]] = {}
    tier_by_code: dict[str, dict[str, str]] = {}
    tier_by_name: dict[str, dict[str, str]] = {}
    for row in tier_rows:
        info = {
            "name": row.get("name") or "",
            "tier": row.get("university_tier") or "",
            "tier_name": row.get("university_tier_name") or "",
            "ruanke_rank": row.get("ruanke_rank") or "",
            "ranking": row.get("ranking") or "",
            "is985": row.get("is985") or "0",
            "is211": row.get("is211") or "0",
            "is_dual_class": row.get("is_dual_class") or "0",
            "school_nature_name": row.get("school_nature_name") or "",
        }
        for key, target in ((row.get("school_id"), tier_by_school_id), (row.get("code"), tier_by_code)):
            key = str(key or "").strip()
            if key and key != "NULL":
                target[key] = info
        name = str(row.get("name") or "").strip()
        if name:
            tier_by_name[name] = info

    local_major_by_code: dict[str, dict[str, str]] = {}
    local_major_by_norm_code: dict[str, dict[str, str]] = {}
    local_major_by_name: dict[str, dict[str, str]] = {}
    for row in local_major_rows:
        code = str(row.get("code") or "").strip().upper()
        name = str(row.get("special_name") or "").strip()
        if code:
            local_major_by_code[code] = row
            local_major_by_norm_code[norm_code(code)] = row
        if name:
            local_major_by_name[name] = row

    examples_by_major: defaultdict[tuple[str, str], dict[str, dict[str, dict[str, str]]]] = defaultdict(lambda: {"1": {}, "2": {}, "3": {}})
    for row in school_major_rows:
        school_id = str(row.get("school_id") or "").strip()
        school_name = str(row.get("school_name") or "").strip()
        info = tier_by_school_id.get(school_id) or tier_by_code.get(school_id) or tier_by_name.get(school_name)
        if not info or info.get("tier") not in {"1", "2", "3"}:
            continue
        tier = info["tier"]
        major_code = norm_code(row.get("major_code"))
        major_name = str(row.get("major_name") or "").strip()
        if major_code:
            examples_by_major[("code", major_code)][tier][school_name] = info
        if major_name:
            examples_by_major[("name", major_name)][tier][school_name] = info

    def get_examples(code: str, name: str, tier: str) -> list[str]:
        bucket: dict[str, dict[str, str]] = {}
        if norm_code(code):
            bucket.update(examples_by_major.get(("code", norm_code(code)), {}).get(tier, {}))
        if name:
            bucket.update(examples_by_major.get(("name", name), {}).get(tier, {}))
        return [school_name for school_name, _ in sorted(bucket.items(), key=sort_school_key)][:5]

    output_rows: list[dict[str, str]] = []
    source_counter: defaultdict[str, int] = defaultdict(int)
    coverage_counter: defaultdict[str, int] = defaultdict(int)
    for row in catalog_rows:
        code = str(row.get("code") or "").strip().upper()
        name = str(row.get("special_name") or "").strip()
        ncode = norm_code(code)
        level2 = str(row.get("level2_name") or "").strip()
        level3 = str(row.get("level3_name") or "").strip()
        major_level = str(row.get("special_type") or row.get("type_name") or "").strip()
        is_vocational = "专科" in major_level or (code.startswith("5") and len(code) >= 5)

        snapshot = intro_by_code.get(code) or intro_by_norm_code.get(ncode) or intro_by_name.get(name)
        local = local_major_by_code.get(code) or local_major_by_norm_code.get(ncode) or local_major_by_name.get(name) or {}
        extracted: list[str] = []
        basis_parts: list[str] = []
        note = ""
        if snapshot:
            extracted = extract_courses((snapshot.get("sections") or {}).get("major_course") or "")
            if extracted:
                basis_parts.append("rysxai_major_course")
            else:
                note = "rysxai课程文本未抽出课程名"
        else:
            note = "未匹配rysxai课程文本"
        if not extracted:
            for key in ("course", "learn_what"):
                extracted.extend(extract_courses(local.get(key) or ""))
            if extracted:
                basis_parts.append("local_edu_major_course_or_learn_what")

        template = pick_template(level3, level2, name, is_vocational)
        core_courses = dedupe_keep_order(extracted + template)[:10]
        if len(extracted) < 5:
            basis_parts.append("category_template")
        basis = "+".join(dict.fromkeys(basis_parts)) or "category_template"
        source_counter[basis] += 1

        t1 = get_examples(code, name, "1")
        t2 = get_examples(code, name, "2")
        t3 = get_examples(code, name, "3")
        for tier, examples in (("1", t1), ("2", t2), ("3", t3)):
            if examples:
                coverage_counter[f"tier{tier}_has_examples"] += 1

        output_rows.append(
            {
                "major_code": code,
                "major_name": name,
                "major_level": major_level,
                "degree": row.get("degree") or "",
                "limit_year": row.get("limit_year") or "",
                "level2_name": level2,
                "level3_name": level3,
                "core_courses_estimated": "、".join(core_courses),
                "course_basis": basis,
                "data_note": note,
                "tier1_school_examples": "、".join(t1) if t1 else "库内未命中",
                "tier1_course_focus": tier_focus("1", t1, level2),
                "tier2_school_examples": "、".join(t2) if t2 else "库内未命中",
                "tier2_course_focus": tier_focus("2", t2, level2),
                "tier3_school_examples": "、".join(t3) if t3 else "库内未命中",
                "tier3_course_focus": tier_focus("3", t3, level2),
            }
        )

    with OUT_CSV.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(output_rows[0].keys()))
        writer.writeheader()
        writer.writerows(output_rows)

    by_name: dict[str, dict[str, str]] = {}
    for row in output_rows:
        by_name.setdefault(row["major_name"], row)
    sample_rows = [by_name[name] for name in SAMPLE_MAJOR_NAMES if name in by_name]
    for row in output_rows:
        if len(sample_rows) >= 32:
            break
        if (
            row["tier1_school_examples"] != "库内未命中"
            and row["tier2_school_examples"] != "库内未命中"
            and row["tier3_school_examples"] != "库内未命中"
            and row not in sample_rows
        ):
            sample_rows.append(row)

    lines = [
        "# 专业核心课程与院校层次样例（抽样版）",
        "",
        "## 方法",
        "- 专业范围：`remote_edu_major_majors_20260614.csv` 的 2053 个专业。",
        "- 院校层次：`remote_edu_university_three_tiers_20260614.csv` 的三类 tier。",
        "- 核心课程：优先从 rysxai `major_course` 爬取文本抽取；不足时用本地 `edu_major.course/learn_what` 和专业类模板补足。",
        "- 学校样例：优先从本地 `edu_university_department_major` 院系专业表匹配到 tier CSV，样例不代表当年招生计划。",
        "",
        "## 覆盖",
        f"- 专业总数：{len(output_rows)}",
        f"- Tier 1 有开设样例的专业：{coverage_counter['tier1_has_examples']}",
        f"- Tier 2 有开设样例的专业：{coverage_counter['tier2_has_examples']}",
        f"- Tier 3 有开设样例的专业：{coverage_counter['tier3_has_examples']}",
        "- 课程来源统计：" + "；".join(f"{key}={value}" for key, value in sorted(source_counter.items())),
        "",
        "## 院校层次总体口径",
    ]
    for row in tier_summary_rows:
        samples = row["sample_schools"].split("、")[:3]
        lines.append(f"- Tier {row['university_tier']} {row['university_tier_name']}：{row['school_count']} 所，样例：{'、'.join(samples)}。")
    lines.extend(
        [
            "",
            "## 抽样专业",
            "| 专业 | 核心课程（估计） | Tier 1 样例 | Tier 2 样例 | Tier 3 样例 | 层次差异判断 |",
            "|---|---|---|---|---|---|",
        ]
    )
    for row in sample_rows[:28]:
        courses = row["core_courses_estimated"]
        if len(courses) > 90:
            courses = courses[:90] + "..."
        lines.append(
            f"| {row['major_name']} | {courses} | {row['tier1_school_examples']} | {row['tier2_school_examples']} | {row['tier3_school_examples']} | Tier1偏理论/科研；Tier2偏行业方向和项目；Tier3偏工具、实训和岗位规范。 |"
        )
    lines.extend(["", f"全量结果见：`{OUT_CSV.as_posix()}`"])
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"output_csv={OUT_CSV}")
    print(f"output_md={OUT_MD}")
    print(f"rows={len(output_rows)}")
    print(f"source_counter={dict(sorted(source_counter.items()))}")
    print(f"coverage_counter={dict(sorted(coverage_counter.items()))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
