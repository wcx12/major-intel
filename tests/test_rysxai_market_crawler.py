import unittest
from tempfile import TemporaryDirectory
from pathlib import Path

from scripts.rysxai_market_crawler import (
    FetchError,
    _write_json,
    build_market_snapshot,
    fetch_json_with_retries,
    list_professions_from_api,
    normalize_job_samples,
    normalize_profession_info,
    should_skip_profession,
    write_profession_list_csv,
)


INFO_PAYLOAD = {
    "code": "SUCCESS",
    "data": {
        "id": 270,
        "name": "机械工程",
        "code": "080201",
        "level": "本科",
        "jobdetail": {
            "1": [
                {"name": "机械重工", "rate": "29.61"},
                {"name": "汽车", "rate": "13.07"},
            ],
            "2": [
                {"area": "上海市", "rate": "15.10"},
                {"area": "北京市", "rate": "13.10"},
            ],
            "3": [
                {
                    "detail_pos": "机械设计/制造",
                    "detail_job": "项目工程师，机械研发工程师，机械制图员",
                    "rate": "21.00",
                }
            ],
        },
        "demand_ranking": {
            "series": [{"data": [61649, 9396], "count": 61649}],
            "categories": ["全国", "上海"],
        },
        "salary_ranking": {
            "series": [{"data": [7516, 8945]}],
            "categories": ["全国", "上海"],
        },
    },
}

POSITIONS_PAYLOAD = {
    "code": "SUCCESS",
    "data": {
        "total": 2,
        "items": [
            {
                "itemId": 50,
                "jobName": "机械工程师",
                "cityName": "无锡",
                "areaDistrict": "惠山区",
                "brandName": "励金",
                "brandIndustry": "通用设备",
                "brandScaleName": "0-20人",
                "brandStageName": "未融资",
                "jobDegree": "本科",
                "jobExperience": "5-10年",
                "salaryDesc": "15-20K",
                "skills": ["Solidworks", "机械设计"],
                "bossName": "曹女士",
                "bossAvatar": "https://example.test/avatar.png",
                "_source": {
                    "salary_raw": "1.5-2万/月",
                    "salary_first": 15000,
                    "salary_last": 20000,
                    "company_name": "励金",
                    "company_tag": ["未融资", "0-20人", "通用设备"],
                },
            },
            {
                "itemId": 47,
                "jobName": "机械工程师",
                "cityName": "上海",
                "areaDistrict": "奉贤区",
                "brandName": "帕孚(上海)",
                "brandIndustry": "仪器仪表",
                "brandScaleName": "20-99人",
                "brandStageName": "",
                "jobDegree": "本科",
                "jobExperience": "3-5年",
                "salaryDesc": "9-14K",
                "skills": ["AutoCAD", "机械工程"],
                "_source": {
                    "salary_raw": "9千-1.4万/月",
                    "salary_first": 9000,
                    "salary_last": 14000,
                    "company_name": "帕孚(上海)",
                    "company_tag": ["", "20-99人", "仪器仪表"],
                },
            },
        ],
    },
}


class RysxaiMarketCrawlerTests(unittest.TestCase):
    def test_normalize_profession_info_extracts_macro_employment_and_rankings(self):
        normalized = normalize_profession_info(INFO_PAYLOAD, "2026-05-19T12:00:00+08:00")

        self.assertEqual(normalized["profession"]["id"], 270)
        self.assertEqual(normalized["profession"]["name"], "机械工程")
        self.assertEqual(
            normalized["macro_employment"]["industry_distribution"][0],
            {"label": "机械重工", "rate_percent": 29.61},
        )
        self.assertEqual(
            normalized["macro_employment"]["region_distribution"][1],
            {"label": "北京市", "rate_percent": 13.1},
        )
        self.assertEqual(
            normalized["macro_employment"]["job_direction_distribution"][0]["detail_jobs"],
            ["项目工程师", "机械研发工程师", "机械制图员"],
        )
        self.assertEqual(
            normalized["demand_ranking"][0],
            {"region": "全国", "demand_count": 61649},
        )
        self.assertEqual(
            normalized["salary_ranking"][1],
            {"region": "上海", "monthly_salary_reference": 8945},
        )

    def test_normalize_job_samples_keeps_safe_fields_only(self):
        samples = normalize_job_samples(POSITIONS_PAYLOAD)

        self.assertEqual(len(samples), 2)
        self.assertEqual(samples[0]["company_name"], "励金")
        self.assertEqual(samples[0]["monthly_salary_min"], 15000)
        self.assertEqual(samples[0]["monthly_salary_max"], 20000)
        self.assertEqual(samples[0]["skills"], ["Solidworks", "机械设计"])
        self.assertNotIn("bossName", samples[0])
        self.assertNotIn("bossAvatar", samples[0])

    def test_build_market_snapshot_adds_caution_and_salary_aggregates(self):
        snapshot = build_market_snapshot(
            INFO_PAYLOAD,
            POSITIONS_PAYLOAD,
            "2026-05-19T12:00:00+08:00",
        )

        self.assertEqual(snapshot["schema_version"], "rysxai_market_snapshot/v1")
        self.assertEqual(snapshot["source"]["source_level"], "C")
        self.assertEqual(
            snapshot["source"]["info_url"],
            "https://api.rysxai.cn/api/ry_education/profession/info/?id=270",
        )
        self.assertEqual(
            snapshot["source"]["positions_url"],
            "https://api.rysxai.cn/api/ry_education/profession/positions/?id=270",
        )
        self.assertEqual(snapshot["job_posting_sample_total_reported"], 2)
        self.assertEqual(snapshot["job_posting_sample_count"], 2)
        self.assertIn("不代表某校某专业毕业生实际薪资", snapshot["warnings"][0])
        self.assertEqual(snapshot["salary_observations_by_city"]["无锡"]["sample_count"], 1)
        self.assertEqual(
            snapshot["salary_observations_by_city"]["无锡"]["monthly_salary_midpoint_avg"],
            17500,
        )
        self.assertEqual(snapshot["job_posting_samples"][1]["city"], "上海")

    def test_write_json_escapes_non_ascii_for_shell_tools(self):
        with TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "sample.json"

            _write_json(output_path, {"name": "机械工程"})

            raw_text = output_path.read_text(encoding="utf-8")
            self.assertIn("\\u673a\\u68b0\\u5de5\\u7a0b", raw_text)
            self.assertNotIn("机械工程", raw_text)

    def test_list_professions_from_api_deduplicates_hot_group(self):
        def fake_fetch(url, timeout_seconds=20):
            if "search/selects" in url:
                return {
                    "code": "SUCCESS",
                    "data": [
                        {
                            "name": "本科",
                            "category_list": [{"name": "工学"}],
                        }
                    ],
                }
            return {
                "code": "SUCCESS",
                "data": [
                    {
                        "subject": "热门",
                        "profession_list": [
                            {
                                "id": 270,
                                "name": "机械工程",
                                "code": "080201",
                                "degree": "工学学士",
                                "limit_year": "四年",
                                "heat": 100,
                            }
                        ],
                    },
                    {
                        "subject": "机械类",
                        "profession_list": [
                            {
                                "id": 270,
                                "name": "机械工程",
                                "code": "080201",
                                "degree": "工学学士",
                                "limit_year": "四年",
                                "heat": 100,
                            },
                            {
                                "id": 271,
                                "name": "机械设计制造及其自动化",
                                "code": "080202",
                                "degree": "工学学士",
                                "limit_year": "四年",
                                "heat": 90,
                            },
                        ],
                    },
                ],
            }

        rows = list_professions_from_api(fetcher=fake_fetch)

        self.assertEqual([row["rysxai_profession_id"] for row in rows], [270, 271])
        self.assertEqual(rows[0]["subject"], "机械类")
        self.assertEqual(rows[0]["is_hot"], "true")
        self.assertEqual(rows[1]["is_hot"], "false")

    def test_write_profession_list_csv_for_batch_input(self):
        with TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "professions.csv"

            write_profession_list_csv(
                [
                    {
                        "rysxai_profession_id": 270,
                        "major_code": "080201",
                        "major_name": "机械工程",
                        "level": "本科",
                        "category": "工学",
                        "subject": "机械类",
                        "degree": "工学学士",
                        "limit_year": "四年",
                        "heat": 100,
                        "is_hot": "true",
                    }
                ],
                output_path,
            )

            text = output_path.read_text(encoding="utf-8-sig")
            self.assertIn("rysxai_profession_id,major_code,major_name", text)
            self.assertIn("270,080201,机械工程", text)

    def test_should_skip_profession_when_resume_output_exists(self):
        with TemporaryDirectory() as temp_dir:
            processed_dir = Path(temp_dir)
            (processed_dir / "profession_270_market_snapshot.json").write_text(
                "{}", encoding="utf-8"
            )

            self.assertTrue(should_skip_profession(270, processed_dir, resume=True))
            self.assertFalse(should_skip_profession(270, processed_dir, resume=False))

    def test_fetch_json_with_retries_retries_transient_errors_only(self):
        calls = []

        def transient_fetch(url, timeout_seconds=20):
            calls.append(url)
            if len(calls) == 1:
                raise FetchError("temporary", status_code=None)
            return {"code": "SUCCESS", "data": {}}

        result = fetch_json_with_retries(
            "https://example.test",
            fetcher=transient_fetch,
            sleeper=lambda seconds: None,
            max_retries=1,
        )

        self.assertEqual(result["code"], "SUCCESS")
        self.assertEqual(len(calls), 2)

        def forbidden_fetch(url, timeout_seconds=20):
            raise FetchError("forbidden", status_code=403)

        with self.assertRaises(FetchError):
            fetch_json_with_retries(
                "https://example.test",
                fetcher=forbidden_fetch,
                sleeper=lambda seconds: None,
                max_retries=3,
            )


if __name__ == "__main__":
    unittest.main()
