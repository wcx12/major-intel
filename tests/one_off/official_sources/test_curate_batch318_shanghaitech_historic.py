import unittest


RECOMMENDATION_2017_HTML = """
<html><body>
<table>
<tr><td rowspan="2">序号</td><td rowspan="2">姓名</td><td colspan="2">拟录取学科专业</td><td rowspan="2">拟录取类型</td></tr>
<tr><td>一级学科</td><td>二级学科</td></tr>
<tr><td>1</td><td>谭静</td><td>化学</td><td>无机化学</td><td>学术型硕士</td></tr>
</table>
</body></html>
"""


MASTER_2017_HTML = """
<html><body>
<table>
<tr><td>序号</td><td>姓名</td><td>拟录取学院</td></tr>
<tr><td>1</td><td>安邦</td><td>物质科学与技术学院</td></tr>
</table>
</body></html>
"""


DOCTOR_2017_HTML = """
<html><body>
<table>
<tr><td>序号</td><td>考生姓名</td><td>录取季别</td></tr>
<tr><td>1</td><td>安柏霖</td><td>2017秋季</td></tr>
</table>
</body></html>
"""


RECOMMENDATION_2018_HTML = """
<html><body>
<table>
<tr><td rowspan="2">序号</td><td rowspan="2">姓名</td><td colspan="2">拟录取学科专业</td><td rowspan="2">拟录取类型</td></tr>
<tr><td>学科代码</td><td>学科名称</td></tr>
<tr><td>1</td><td>曾腾正</td><td>070300</td><td>化学</td><td>学术型硕士</td></tr>
</table>
</body></html>
"""


class Batch318ShanghaiTechHistoricCurationTests(unittest.TestCase):
    def test_curates_all_supported_html_table_shapes(self):
        from scripts.one_off.official_sources.curate_batch318_shanghaitech_historic import (
            PAGE_CONFIGS,
            curate_html_records,
        )

        rows = []
        rows.extend(curate_html_records(RECOMMENDATION_2017_HTML, PAGE_CONFIGS[0]))
        rows.extend(curate_html_records(MASTER_2017_HTML, PAGE_CONFIGS[1]))
        rows.extend(curate_html_records(DOCTOR_2017_HTML, PAGE_CONFIGS[2]))
        rows.extend(curate_html_records(RECOMMENDATION_2018_HTML, PAGE_CONFIGS[3]))

        self.assertEqual(len(rows), 4)
        self.assertTrue(all(row["school_name"] == "上海科技大学" for row in rows))
        self.assertFalse(any(row["needs_review"] for row in rows))

        recommendation = rows[0]
        self.assertEqual(recommendation["year"], 2017)
        self.assertEqual(recommendation["route"], "recommendation_exemption")
        self.assertEqual(recommendation["person_name"], "谭静")
        self.assertEqual(recommendation["admission_major"], "化学")
        self.assertIn("second_level_subject: 无机化学", recommendation["remarks"])
        self.assertIn("admission_type: 学术型硕士", recommendation["remarks"])

        master = rows[1]
        self.assertEqual(master["route"], "postgraduate_exam_or_admission")
        self.assertEqual(master["person_name"], "安邦")
        self.assertEqual(master["college"], "物质科学与技术学院")
        self.assertIn("source_columns: 序号/姓名/拟录取学院", master["remarks"])

        doctor = rows[2]
        self.assertEqual(doctor["person_name"], "安柏霖")
        self.assertIn("degree_level: 博士", doctor["remarks"])
        self.assertIn("admission_season: 2017秋季", doctor["remarks"])

        recommendation_2018 = rows[3]
        self.assertEqual(recommendation_2018["year"], 2018)
        self.assertEqual(recommendation_2018["person_name"], "曾腾正")
        self.assertEqual(recommendation_2018["admission_major"], "化学")
        self.assertIn("subject_code: 070300", recommendation_2018["remarks"])

    def test_skips_header_rows_and_bad_status_fragments(self):
        from scripts.one_off.official_sources.curate_batch318_shanghaitech_historic import PAGE_CONFIGS, curate_html_records

        rows = curate_html_records(RECOMMENDATION_2017_HTML, PAGE_CONFIGS[0])

        self.assertEqual([row["person_name"] for row in rows], ["谭静"])
        flattened_status_fields = "\n".join(
            " ".join(str(row.get(field, "")) for field in ("remarks", "quality_flags"))
            for row in rows
        )
        for bad_fragment in ("进入复试名单", "拟不录取", "不予录取", "候补", "放弃", "未参加复试"):
            self.assertNotIn(bad_fragment, flattened_status_fields)


if __name__ == "__main__":
    unittest.main()
