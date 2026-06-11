import unittest
from unittest.mock import AsyncMock, patch

from app.api.v1.endpoints.ai import assess
from app.models.models import Lead
from app.schemas.schemas import AIAssessmentRequest


class FakeSession:
    def __init__(self, lead):
        self.lead = lead
        self.get_calls = []

    async def get(self, model, object_id):
        self.get_calls.append((model, object_id))
        return self.lead


class AIAssessmentEndpointTests(unittest.IsolatedAsyncioTestCase):
    async def test_ai_assess_endpoint_persists_assessment(self):
        lead = Lead(
            id="lead-1",
            first_name="Ada",
            last_name="Lovelace",
            email="ada@example.com",
        )
        db = FakeSession(lead)
        payload = AIAssessmentRequest(lead_id="lead-1", context_notes="extra context")
        persisted = {"ai_score": 91}

        with patch(
            "app.api.v1.endpoints.ai.assess_and_persist_lead",
            new=AsyncMock(return_value=persisted),
        ) as assess_and_persist_lead:
            result = await assess(payload, db=db)

        self.assertEqual(result, persisted)
        self.assertEqual(db.get_calls, [(Lead, "lead-1")])
        assess_and_persist_lead.assert_awaited_once_with(db, lead, "extra context")


if __name__ == "__main__":
    unittest.main()
