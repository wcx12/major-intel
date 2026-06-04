import unittest


class Batch524BjfuResultSystemTests(unittest.TestCase):
    def test_curate_result_html_extracts_bjfu_recommendation_rows(self):
        from scripts.one_off.official_sources.curate_batch524_bjfu_result_system import curate_result_html

        html = """
        <html>
          <head><title>北京林业大学硕士推免预报名系统</title></head>
          <body>
            <a href="/result/result/formalResult">拟录取公示</a>
            <table>
              <tr>
                <th>id</th><th>姓名</th><th>身份证号</th><th>学院</th>
                <th>专业编码号</th><th>专业</th><th>总分</th><th>状态</th>
              </tr>
              <tr>
                <td>1</td><td>饶**</td><td>511526***0342</td><td>林学院</td>
                <td>070503</td><td>地图学与地理信息系统</td><td>67.72</td><td>拟录取</td>
              </tr>
              <tr>
                <td>2</td><td>张**</td><td>110101***1234</td><td>草业与草原学院</td>
                <td>095131</td><td>农艺与种业</td><td>85.99</td><td>拟录取</td>
              </tr>
            </table>
          </body>
        </html>
        """

        rows = curate_result_html(html, source_url="http://tm.yzb.bjfu.edu.cn/result")

        self.assertEqual(len(rows), 2)
        first = rows[0]
        self.assertEqual(first["school_name"], "北京林业大学")
        self.assertEqual(first["year"], 2026)
        self.assertEqual(first["document_type"], "incoming_recommendation_admission_list")
        self.assertEqual(first["route"], "recommendation_exemption")
        self.assertEqual(first["person_name"], "饶**")
        self.assertEqual(first["student_id"], "511526***0342")
        self.assertEqual(first["college"], "林学院")
        self.assertEqual(first["admission_major"], "地图学与地理信息系统")
        self.assertEqual(first["ranking"], "1")
        self.assertIn("major_code 070503", first["remarks"])
        self.assertIn("total_score 67.72", first["remarks"])
        self.assertIn("status 拟录取", first["remarks"])
        self.assertEqual(first["source_url"], "http://tm.yzb.bjfu.edu.cn/result")
        self.assertIn("拟录取公示", first["title"])


if __name__ == "__main__":
    unittest.main()
