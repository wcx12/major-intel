import unittest

from scripts.datasets.build_ai_replacement_dataset import (
    build_major_profiles,
    extract_candidate_evidence,
    aggregate_candidates,
    score_job_title,
)


class AiReplacementDatasetTests(unittest.TestCase):
    def test_extract_candidate_evidence_prefers_detail_jobs_and_filters_noise(self):
        snapshot = {
            "profession": {
                "id": 1,
                "code": "050301",
                "name": "新闻学",
                "level": "本科",
            },
            "macro_employment": {
                "job_direction_distribution": [
                    {
                        "label": "内容运营",
                        "rate_percent": 40,
                        "detail_jobs": ["新媒体运营，文案编辑，其他"],
                    }
                ],
                "industry_distribution": [
                    {"label": "互联网", "rate_percent": 30},
                    {"label": "其他", "rate_percent": 70},
                ],
            },
            "job_posting_samples": [
                {"job_title": "文案策划", "skills": ["内容生产", "选题策划"]}
            ],
        }

        evidence = extract_candidate_evidence(snapshot)
        titles = {item.normalized_job_title for item in evidence}

        self.assertIn("新媒体运营", titles)
        self.assertIn("文案编辑", titles)
        self.assertIn("文案策划", titles)
        self.assertNotIn("其他", titles)

    def test_score_job_title_applies_china_barrier_adjustment(self):
        editor = score_job_title("文案编辑")
        doctor = score_job_title("临床医师")
        operator = score_job_title("数控操作工")

        self.assertGreater(editor.final_job_risk_score, 70)
        self.assertGreater(editor.ai_exposure_score, 85)
        self.assertLess(doctor.final_job_risk_score, editor.final_job_risk_score)
        self.assertGreaterEqual(doctor.license_barrier_score, 80)
        self.assertLess(operator.final_job_risk_score, 40)
        self.assertGreaterEqual(operator.physical_barrier_score, 80)

    def test_build_major_profiles_ranks_text_major_above_field_major(self):
        snapshots = [
            {
                "profession": {
                    "id": 1,
                    "code": "050301",
                    "name": "新闻学",
                    "level": "本科",
                },
                "macro_employment": {
                    "job_direction_distribution": [
                        {
                            "label": "内容运营",
                            "rate_percent": 80,
                            "detail_jobs": ["文案编辑，新媒体运营"],
                        }
                    ]
                },
                "job_posting_samples": [],
            },
            {
                "profession": {
                    "id": 2,
                    "code": "520201",
                    "name": "护理",
                    "level": "专科",
                },
                "macro_employment": {
                    "job_direction_distribution": [
                        {
                            "label": "护理",
                            "rate_percent": 80,
                            "detail_jobs": ["护士，护理员"],
                        }
                    ]
                },
                "job_posting_samples": [],
            },
        ]
        evidence = []
        for snapshot in snapshots:
            evidence.extend(extract_candidate_evidence(snapshot))

        profiles, _, _ = build_major_profiles(aggregate_candidates(evidence))
        by_name = {profile.major_name: profile for profile in profiles}

        self.assertGreater(
            by_name["新闻学"].ai_replacement_score,
            by_name["护理"].ai_replacement_score,
        )
        self.assertEqual(profiles[0].major_name, "新闻学")


if __name__ == "__main__":
    unittest.main()
