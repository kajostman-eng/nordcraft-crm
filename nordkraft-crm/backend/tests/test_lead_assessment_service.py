import asyncio
import unittest
from datetime import datetime

from app.services.lead_assessment_service import assess_and_persist_lead


class FakeDB:
    def __init__(self):
        self.committed = False

    async def commit(self):
        self.committed = True


class FakeLead:
    pass


class LeadAssessmentServiceTests(unittest.TestCase):
    def test_assess_and_persist_lead_updates_all_score_fields(self):
        async def runner(lead, context_notes):
            self.assertIs(lead, fake_lead)
            self.assertEqual(context_notes, "call notes")
            return {
                "ai_score": 87,
                "automation_readiness": 91,
                "ai_maturity_level": 4,
                "estimated_time_savings_hrs": 420,
                "estimated_roi_multiplier": 5.5,
                "key_opportunities": ["intake automation"],
                "recommended_phases": [{"phase": 1}],
                "summary": "Strong fit.",
            }

        fake_db = FakeDB()
        fake_lead = FakeLead()

        assessment = asyncio.run(
            assess_and_persist_lead(fake_db, fake_lead, "call notes", runner=runner)
        )

        self.assertTrue(fake_db.committed)
        self.assertEqual(fake_lead.ai_score, 87)
        self.assertEqual(fake_lead.automation_readiness, 91)
        self.assertEqual(fake_lead.ai_maturity_level, 4)
        self.assertEqual(fake_lead.estimated_time_savings_hrs, 420)
        self.assertEqual(fake_lead.estimated_roi_multiplier, 5.5)
        self.assertIs(fake_lead.ai_assessment_json, assessment)
        self.assertIsInstance(fake_lead.last_assessed_at, datetime)


if __name__ == "__main__":
    unittest.main()
