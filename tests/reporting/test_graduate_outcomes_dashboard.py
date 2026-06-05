from __future__ import annotations

import html
import importlib.util
import json
from pathlib import Path
import re
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]


def load_dashboard_builder():
    builder_path = ROOT / "scripts" / "build_graduate_outcomes_dashboard.py"
    spec = importlib.util.spec_from_file_location("graduate_outcomes_dashboard_builder", builder_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load dashboard builder from {builder_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class GraduateOutcomesDashboardTest(unittest.TestCase):
    def test_static_dashboard_reconciles_package_metrics_and_embeds_compact_data(self) -> None:
        builder = load_dashboard_builder()

        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "index.html"
            result = builder.build_dashboard(ROOT, output_path)

            self.assertTrue(output_path.exists())
            self.assertLess(output_path.stat().st_size, 3_000_000)

            page = output_path.read_text(encoding="utf-8")
            self.assertIn("研究生去向数据看板", page)
            self.assertIn("285,608", page)
            self.assertNotIn("NaN", page)
            self.assertNotIn("undefined", page)

            match = re.search(
                r'<script id="dashboard-data" type="application/json">(.*?)</script>',
                page,
                re.S,
            )
            self.assertIsNotNone(match, "dashboard should embed bounded JSON data")
            dashboard_data = json.loads(html.unescape(match.group(1)))

        metrics = result["metrics"]
        self.assertEqual(metrics["target_schools"], 430)
        self.assertEqual(metrics["covered_schools"], 425)
        self.assertEqual(metrics["uncovered_schools"], 5)
        self.assertEqual(metrics["public_records"], 285608)
        self.assertAlmostEqual(metrics["coverage_rate"], 425 / 430)

        self.assertEqual(dashboard_data["metrics"], metrics)
        self.assertGreaterEqual(len(dashboard_data["charts"]["records_by_year"]), 1)
        self.assertGreaterEqual(len(dashboard_data["tables"]["coverage_by_province"]), 1)

        blocker_names = {row["school_name"] for row in dashboard_data["tables"]["blockers"]}
        self.assertEqual(
            blocker_names,
            {
                "北京电影学院",
                "成都体育学院",
                "宁波诺丁汉大学",
                "西藏农牧大学",
                "重庆邮电大学",
            },
        )

