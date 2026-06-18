import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from scripts.rysxai_major_intro_crawler import (
    crawl_major_intro_batch,
    intro_snapshot_to_csv_row,
    normalize_major_intro,
)


INFO_PAYLOAD = {
    "code": "SUCCESS",
    "data": {
        "id": 270,
        "name": "机械工程",
        "code": "080201",
        "level": "本科",
        "degree": "工学学士",
        "limit_year": "四年",
        "sel_adv": "物理+化学",
        "enrollment_scale": "20000-22000人",
        "gender_ratio": {"女生": "9", "男生": "91"},
        "NCEE_ratio": {"文科": "1", "理科": "99"},
        "content": "# 机械工程专业解析",
        "course": "# 机械工程课程分析",
        "master_prof": "# 机械工程 → 主流衔接研究生专业分类",
        "similar_prof": "#### 机械工程相似专业",
        "featured_video_id": 6178,
        "featured_video_title": "机械类专业讲解",
        "profession_intro": [
            {
                "id": 7079,
                "title": "机械工程介绍",
                "video_url": "https://source.rysxai.cn/video/sample.mp4",
            }
        ],
        "univ_count": 143,
        "apply_plan_ratio": 118,
    },
}


class RysxaiMajorIntroCrawlerTests(unittest.TestCase):
    def test_normalize_major_intro_maps_required_sections(self):
        snapshot = normalize_major_intro(INFO_PAYLOAD, "2026-06-11T12:00:00+08:00")

        self.assertEqual(snapshot["schema_version"], "rysxai_major_introduction_snapshot/v1")
        self.assertEqual(snapshot["profession"]["id"], 270)
        self.assertEqual(snapshot["sections"]["major_detail"], "# 机械工程专业解析")
        self.assertEqual(snapshot["sections"]["major_course"], "# 机械工程课程分析")
        self.assertEqual(
            snapshot["sections"]["undergraduate_to_graduate"],
            "# 机械工程 → 主流衔接研究生专业分类",
        )
        self.assertEqual(snapshot["sections"]["similar_majors"], "#### 机械工程相似专业")
        self.assertEqual(snapshot["section_source_fields"]["major_detail"], "content")
        self.assertEqual(snapshot["warnings"], [])
        self.assertEqual(snapshot["profession_intro_videos"][0]["id"], 7079)

    def test_normalize_major_intro_falls_back_to_ai_fields(self):
        payload = {
            "code": "SUCCESS",
            "data": {
                "id": 1,
                "name": "样例专业",
                "ai_info": "详情",
                "ai_course": "课程",
                "ai_master_prof": "衔接",
                "ai_similar_prof": "相似",
            },
        }

        snapshot = normalize_major_intro(payload, "2026-06-11T12:00:00+08:00")

        self.assertEqual(snapshot["sections"]["major_detail"], "详情")
        self.assertEqual(snapshot["section_source_fields"]["major_detail"], "ai_info")
        self.assertEqual(snapshot["warnings"], [])

    def test_intro_snapshot_to_csv_row_flattens_sections(self):
        snapshot = normalize_major_intro(INFO_PAYLOAD, "2026-06-11T12:00:00+08:00")

        row = intro_snapshot_to_csv_row(snapshot)

        self.assertEqual(row["rysxai_profession_id"], 270)
        self.assertEqual(row["major_name"], "机械工程")
        self.assertEqual(row["major_course"], "# 机械工程课程分析")
        self.assertIn("profession/info/?id=270", row["info_url"])

    def test_crawl_major_intro_batch_writes_snapshots_and_aggregates(self):
        def fake_fetch(url, timeout_seconds=20):
            return INFO_PAYLOAD

        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            manifest = crawl_major_intro_batch(
                [{"rysxai_profession_id": 270}],
                raw_dir=root / "raw",
                processed_dir=root / "processed",
                logs_dir=root / "logs",
                sleep_seconds=0,
                run_id="test-run",
                fetcher=fake_fetch,
                sleeper=lambda seconds: None,
            )

            snapshot_path = root / "processed" / "profession_270_major_intro_snapshot.json"
            self.assertTrue(snapshot_path.exists())
            self.assertEqual(manifest["success_count"], 1)
            self.assertEqual(manifest["failure_count"], 0)

            jsonl_path = Path(manifest["aggregate_jsonl"])
            csv_path = Path(manifest["aggregate_csv"])
            self.assertTrue(jsonl_path.exists())
            self.assertTrue(csv_path.exists())
            jsonl_rows = [
                json.loads(line)
                for line in jsonl_path.read_text(encoding="utf-8").splitlines()
            ]
            self.assertEqual(jsonl_rows[0]["profession"]["name"], "机械工程")
            csv_text = csv_path.read_text(encoding="utf-8-sig")
            self.assertIn("major_detail,major_course", csv_text)
            self.assertIn("# 机械工程课程分析", csv_text)


if __name__ == "__main__":
    unittest.main()
