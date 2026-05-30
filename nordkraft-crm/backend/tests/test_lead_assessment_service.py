import unittest

from app.models.models import Lead
from app.services import lead_assessment_service


ASSESSMENT = {
    "ai_score": 87,
    "automation_readiness": 81,
    "ai_maturity_level": 4,
    "estimated_time_savings_hrs": 240,
    "estimated_roi_multiplier": 5.2,
    "key_opportunities": ["Intake automation"],
    "recommended_phases": [{"phase": 1, "name": "Quick wins"}],
    "summary": "Strong automation opportunity.",
}


class _FakeDb:
    def __init__(self):
        self.committed = False
        self.refreshed = None

    async def commit(self):
        self.committed = True

    async def refresh(self, lead):
        self.refreshed = lead


class LeadAssessmentServiceTests(unittest.IsolatedAsyncioTestCase):
    async def test_assessment_fields_are_persisted_to_lead(self):
        original = lead_assessment_service.run_ai_assessment

        async def fake_run_ai_assessment(lead, context_notes=""):
            self.assertEqual(lead.email, "lead@example.com")
            self.assertEqual(context_notes, "sales call notes")
            return ASSESSMENT

        lead_assessment_service.run_ai_assessment = fake_run_ai_assessment
        try:
            db = _FakeDb()
            lead = Lead(first_name="Ada", last_name="Lovelace", email="lead@example.com")

            result = await lead_assessment_service.assess_and_persist_lead(db, lead, "sales call notes")
        finally:
            lead_assessment_service.run_ai_assessment = original

        self.assertEqual(result, ASSESSMENT)
        self.assertEqual(lead.ai_score, 87)
        self.assertEqual(lead.automation_readiness, 81)
        self.assertEqual(lead.ai_maturity_level, 4)
        self.assertEqual(lead.estimated_time_savings_hrs, 240)
        self.assertEqual(lead.estimated_roi_multiplier, 5.2)
        self.assertEqual(lead.ai_assessment_json, ASSESSMENT)
        self.assertIsNotNone(lead.last_assessed_at)
        self.assertTrue(db.committed)
        self.assertIs(db.refreshed, lead)


if __name__ == "__main__":
    unittest.main()
