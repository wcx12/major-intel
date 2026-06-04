import unittest

from scripts.one_off.official_sources.curate_batch451_njust_2024_doctor_html import curate_records, parse_table_rows


class CurateBatch451Njust2024DoctorHtmlTests(unittest.TestCase):
    def test_parse_table_rows_keeps_only_admission_table_people(self):
        html = """
        <table>
          <tr><td>序号</td><td>拟录取学院</td><td>拟录取专业代码</td><td>拟录取专业名称</td><td>姓名</td><td>备注</td></tr>
          <tr><td>1</td><td>化学与化工学院</td><td>080500</td><td>材料科学与工程</td><td>温彦威</td><td></td></tr>
          <tr><td>2</td><td>化学与化工学院</td><td>080500</td><td>材料科学与工程</td><td>周远亮</td><td></td></tr>
        </table>
        <table>
          <tr><td>人事处</td><td>电子信箱</td></tr>
        </table>
        """

        records = parse_table_rows(html)

        self.assertEqual([record["person_name"] for record in records], ["温彦威", "周远亮"])
        self.assertEqual(records[0]["college"], "化学与化工学院")
        self.assertEqual(records[0]["major"], "080500")
        self.assertEqual(records[0]["admission_major"], "080500 材料科学与工程")
        self.assertEqual(records[0]["ranking"], "1")

    def test_curate_records_extracts_three_real_rows_from_raw_page(self):
        rows = curate_records()

        self.assertEqual(len(rows), 3)
        self.assertEqual([row["person_name"] for row in rows], ["温彦威", "周远亮", "苏玉静"])
        self.assertTrue(all(row["school_name"] == "南京理工大学" for row in rows))
        self.assertTrue(all(row["document_type"] == "postgraduate_admission_list" for row in rows))
        self.assertFalse(any(row["person_name"] in {"人事处", "体育部", "保卫处"} for row in rows))


if __name__ == "__main__":
    unittest.main()
