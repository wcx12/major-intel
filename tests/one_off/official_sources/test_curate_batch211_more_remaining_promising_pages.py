import unittest
from pathlib import Path


class Batch211MoreRemainingPromisingPagesCurationTests(unittest.TestCase):
    def test_curate_tongji_dentistry_table_keeps_admitted_rows(self):
        from scripts.one_off.official_sources.curate_batch211_more_remaining_promising_pages import curate_tongji_dentistry_html

        rows = curate_tongji_dentistry_html(
            Path(
                "data/raw/graduate_outcomes_official_site_websearch_web_20260528_batch211_more_remaining_promising_pages/"
                "dent.tongji.edu.cn/9a91fbf5cdc02e9d.htm"
            )
        )

        self.assertEqual(len(rows), 34)
        self.assertEqual({row["school_name"] for row in rows}, {"同济大学"})
        self.assertEqual({row["college"] for row in rows}, {"口腔医学院"})
        self.assertEqual({row["document_type"] for row in rows}, {"recommendation_exemption_list"})
        self.assertEqual({row["route"] for row in rows}, {"recommendation_exemption"})
        self.assertFalse(any(row["needs_review"] for row in rows))

        first = rows[0]
        self.assertEqual(first["ranking"], "1")
        self.assertEqual(first["person_name"], "李露")
        self.assertIn("qualification_type 学硕", first["remarks"])
        self.assertIn("retest_total 292", first["remarks"])
        self.assertIn("admission_status 拟录取", first["remarks"])

        veteran = rows[3]
        self.assertEqual(veteran["person_name"], "魏云霄")
        self.assertIn("note 退伍军人", veteran["remarks"])

        last = rows[-1]
        self.assertEqual(last["ranking"], "34")
        self.assertEqual(last["person_name"], "布威海丽且姆·瓦日斯")
        self.assertIn("qualification_type 专硕", last["remarks"])


if __name__ == "__main__":
    unittest.main()
