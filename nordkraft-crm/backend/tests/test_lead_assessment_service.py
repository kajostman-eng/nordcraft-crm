import unittest
from unittest.mock import AsyncMock, patch

from app.models.models import Lead
from app.services.lead_assessment_service import assess_and_persist_lead, auto_score_lead


ASSESSMENT = {
    "ai_score": 87,
    "automation_readiness": 78,
    "ai_maturity_level": 3,
    "estimated_time_savings_hrs": 420,
    "estimated_roi_multiplier": 4.2,
    "key_opportunities": ["Lead routing", "Invoice automation"],
    "recommended_phases": [],
    "summary": "Strong automation fit.",
}


class FakeSession:
    def __init__(self, lead=None):
        self.lead = lead
        self.commit_count = 0
        self.rollback_count = 0
        self.get_calls = []

    async def commit(self):
        self.commit_count += 1

    async def rollback(self):
        self.rollback_count += 1

    async def get(self, model, object_id):
        self.get_calls.append((model, object_id))
        return self.lead


class FakeSessionContext:
    def __init__(self, session):
        self.session = session

    async def __aenter__(self):
        return self.session

    async def __aexit__(self, exc_type, exc, tb):
        return False


class LeadAssessmentServiceTests(unittest.IsolatedAsyncioTestCase):
    async def test_assess_and_persist_lead_updates_score_fields(self):
        lead = Lead(
            id="lead-1",
            first_name="Ada",
            last_name="Lovelace",
            email="ada@example.com",
        )
        db = FakeSession(lead)

        with patch(
            "app.services.lead_assessment_service.run_ai_assessment",
            new=AsyncMock(return_value=ASSESSMENT),
        ) as run_ai_assessment:
            result = await assess_and_persist_lead(db, lead, "context")

        self.assertEqual(result, ASSESSMENT)
        run_ai_assessment.assert_awaited_once_with(lead, "context")
        self.assertEqual(lead.ai_score, ASSESSMENT["ai_score"])
        self.assertEqual(lead.automation_readiness, ASSESSMENT["automation_readiness"])
        self.assertEqual(lead.ai_maturity_level, ASSESSMENT["ai_maturity_level"])
        self.assertEqual(lead.estimated_time_savings_hrs, ASSESSMENT["estimated_time_savings_hrs"])
        self.assertEqual(lead.estimated_roi_multiplier, ASSESSMENT["estimated_roi_multiplier"])
        self.assertEqual(lead.ai_assessment_json, ASSESSMENT)
        self.assertIsNotNone(lead.last_assessed_at)
        self.assertEqual(db.commit_count, 1)

    async def test_auto_score_lead_uses_fresh_session(self):
        lead = Lead(
            id="lead-2",
            first_name="Grace",
            last_name="Hopper",
            email="grace@example.com",
        )
        db = FakeSession(lead)

        with (
            patch(
                "app.services.lead_assessment_service.AsyncSessionLocal",
                return_value=FakeSessionContext(db),
            ) as session_factory,
            patch(
                "app.services.lead_assessment_service.run_ai_assessment",
                new=AsyncMock(return_value=ASSESSMENT),
            ),
        ):
            await auto_score_lead("lead-2")

        session_factory.assert_called_once_with()
        self.assertEqual(db.get_calls, [(Lead, "lead-2")])
        self.assertEqual(lead.ai_score, ASSESSMENT["ai_score"])
        self.assertEqual(db.commit_count, 1)
        self.assertEqual(db.rollback_count, 0)


if __name__ == "__main__":
    unittest.main()
