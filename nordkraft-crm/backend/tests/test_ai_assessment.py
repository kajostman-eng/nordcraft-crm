from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, patch

from app.api.v1.endpoints.ai import assess
from app.models.models import Lead
from app.schemas.schemas import AIAssessmentRequest


class FakeSession:
    def __init__(self, lead):
        self.lead = lead
        self.committed = False

    async def get(self, model, item_id):
        if model is Lead and item_id == self.lead.id:
            return self.lead
        return None

    async def commit(self):
        self.committed = True


class AIAssessmentTests(IsolatedAsyncioTestCase):
    async def test_ai_assess_persists_returned_assessment_to_lead(self):
        lead = Lead(
            id="lead-1",
            first_name="Ada",
            last_name="Lovelace",
            email="ada@example.com",
            company_name="Analytical Engines",
            estimated_value=12000,
        )
        db = FakeSession(lead)
        assessment = {
            "ai_score": 88,
            "automation_readiness": 91,
            "ai_maturity_level": 4,
            "estimated_time_savings_hrs": 320,
            "estimated_roi_multiplier": 5.5,
            "key_opportunities": ["Lead triage"],
            "recommended_phases": [{"phase": 1, "name": "Quick wins"}],
            "summary": "Strong fit for automation.",
        }

        with patch(
            "app.services.lead_assessment_service.run_ai_assessment",
            new=AsyncMock(return_value=assessment),
        ) as run_ai_assessment:
            result = await assess(
                AIAssessmentRequest(lead_id=lead.id, context_notes="CRM notes"),
                db=db,
            )

        self.assertEqual(result, assessment)
        self.assertTrue(db.committed)
        self.assertEqual(lead.ai_score, 88)
        self.assertEqual(lead.automation_readiness, 91)
        self.assertEqual(lead.ai_maturity_level, 4)
        self.assertEqual(lead.estimated_time_savings_hrs, 320)
        self.assertEqual(lead.estimated_roi_multiplier, 5.5)
        self.assertEqual(lead.ai_assessment_json, assessment)
        self.assertIsNotNone(lead.last_assessed_at)
        run_ai_assessment.assert_awaited_once_with(lead, "CRM notes")
