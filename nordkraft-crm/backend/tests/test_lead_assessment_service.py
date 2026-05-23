import unittest
from datetime import datetime

from app.services.lead_assessment_service import apply_ai_assessment


class LeadAssessmentServiceTest(unittest.TestCase):
    def test_apply_ai_assessment_updates_score_fields(self):
        lead = type("LeadStub", (), {})()
        assessment = {
            "ai_score": 87,
            "automation_readiness": 74,
            "ai_maturity_level": 4,
            "estimated_time_savings_hrs": 120,
            "estimated_roi_multiplier": 3.5,
            "summary": "Strong fit",
        }

        apply_ai_assessment(lead, assessment)

        self.assertEqual(lead.ai_score, 87)
        self.assertEqual(lead.automation_readiness, 74)
        self.assertEqual(lead.ai_maturity_level, 4)
        self.assertEqual(lead.estimated_time_savings_hrs, 120)
        self.assertEqual(lead.estimated_roi_multiplier, 3.5)
        self.assertIs(lead.ai_assessment_json, assessment)
        self.assertIsInstance(lead.last_assessed_at, datetime)


if __name__ == "__main__":
    unittest.main()
