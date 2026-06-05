import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from scripts.rysxai_market_report import render_markdown_report, write_markdown_report


SNAPSHOT = {
    "schema_version": "rysxai_market_snapshot/v1",
    "captured_at": "2026-05-19T16:48:45+08:00",
    "source": {
        "name": "rysxai",
        "source_level": "C",
        "data_scope": "major_level_market_observation",
    },
    "profession": {
        "id": 270,
        "name": "机械工程",
        "code": "080201",
        "level": "本科",
    },
    "macro_employment": {
        "industry_distribution": [
            {"label": "机械重工", "rate_percent": 29.61},
            {"label": "汽车", "rate_percent": 13.07},
        ],
        "region_distribution": [
            {"label": "上海市", "rate_percent": 15.1},
            {"label": "北京市", "rate_percent": 13.1},
        ],
        "job_direction_distribution": [
            {
                "label": "机械设计/制造",
                "rate_percent": 21.0,
                "detail_jobs": ["项目工程师", "机械研发工程师"],
            }
        ],
    },
    "demand_ranking": [
        {"region": "全国", "demand_count": 61649},
        {"region": "上海", "demand_count": 9396},
    ],
    "salary_ranking": [
        {"region": "全国", "monthly_salary_reference": 7516},
        {"region": "上海", "monthly_salary_reference": 8945},
    ],
    "job_posting_sample_total_reported": 50,
    "job_posting_sample_count": 2,
    "job_posting_samples": [
        {
            "job_title": "机械工程师",
            "company_name": "励金",
            "city": "无锡",
            "industry": "通用设备",
            "salary_raw": "1.5-2万/月",
            "education": "本科",
            "experience": "5-10年",
        },
        {
            "job_title": "机械工程师",
            "company_name": "帕孚(上海)",
            "city": "上海",
            "industry": "仪器仪表",
            "salary_raw": "9千-1.4万/月",
            "education": "本科",
            "experience": "3-5年",
        },
    ],
    "salary_observations_by_city": {
        "上海": {
            "sample_count": 1,
            "monthly_salary_min_observed": 9000,
            "monthly_salary_max_observed": 14000,
            "monthly_salary_midpoint_avg": 11500,
        }
    },
    "warnings": ["招聘岗位和薪资样本只能作为专业市场观察，不代表某校某专业毕业生实际薪资或就业去向。"],
}


class RysxaiMarketReportTests(unittest.TestCase):
    def test_render_markdown_report_contains_human_readable_tables(self):
        markdown = render_markdown_report(SNAPSHOT, top_n=2)

        self.assertIn("# 机械工程 市场观察报告", markdown)
        self.assertIn("| 行业 | 占比 |", markdown)
        self.assertIn("| 机械重工 | 29.61% |", markdown)
        self.assertIn("| 上海 | 8945 |", markdown)
        self.assertIn("| 机械工程师 | 励金 | 无锡 | 通用设备 | 1.5-2万/月 | 本科 | 5-10年 |", markdown)
        self.assertIn("来源等级：C", markdown)
        self.assertIn("不能代表某校某专业毕业生实际薪资", markdown)

    def test_write_markdown_report_uses_bom_for_windows_readability(self):
        with TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "report.md"

            write_markdown_report(SNAPSHOT, output_path)

            raw = output_path.read_bytes()
            self.assertTrue(raw.startswith(b"\xef\xbb\xbf"))
            self.assertIn("机械工程 市场观察报告", output_path.read_text(encoding="utf-8-sig"))


if __name__ == "__main__":
    unittest.main()
