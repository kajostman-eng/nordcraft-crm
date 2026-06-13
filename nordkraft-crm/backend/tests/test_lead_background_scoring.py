import asyncio
import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from app.api.v1.endpoints import leads


_ASSESSMENT = {
    "ai_score": 91,
    "automation_readiness": 83,
    "ai_maturity_level": 4,
    "estimated_time_savings_hrs": 120,
    "estimated_roi_multiplier": 5.2,
}


class _FakeSession:
    def __init__(self, lead=None):
        self.lead = lead
        self.committed = False
        self.rolled_back = False

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def get(self, _model, lead_id):
        self.loaded_lead_id = lead_id
        return self.lead

    async def commit(self):
        self.committed = True

    async def rollback(self):
        self.rolled_back = True


class LeadBackgroundScoringTests(unittest.TestCase):
    def test_auto_score_uses_fresh_session_and_persists_assessment(self):
        lead = SimpleNamespace()
        session = _FakeSession(lead=lead)

        with patch.object(leads, "AsyncSessionLocal", return_value=session):
            with patch.object(leads, "run_ai_assessment", new=AsyncMock(return_value=_ASSESSMENT)):
                asyncio.run(leads._auto_score_lead("lead-123"))

        self.assertEqual(session.loaded_lead_id, "lead-123")
        self.assertTrue(session.committed)
        self.assertFalse(session.rolled_back)
        self.assertEqual(lead.ai_score, 91)
        self.assertEqual(lead.automation_readiness, 83)
        self.assertEqual(lead.ai_maturity_level, 4)
        self.assertEqual(lead.estimated_time_savings_hrs, 120)
        self.assertEqual(lead.estimated_roi_multiplier, 5.2)
        self.assertEqual(lead.ai_assessment_json, _ASSESSMENT)
        self.assertIsNotNone(lead.last_assessed_at)

    def test_auto_score_rolls_back_and_surfaces_failures(self):
        lead = SimpleNamespace()
        session = _FakeSession(lead=lead)

        with patch.object(leads, "AsyncSessionLocal", return_value=session):
            with patch.object(leads, "run_ai_assessment", new=AsyncMock(side_effect=RuntimeError("AI failed"))):
                with self.assertRaises(RuntimeError):
                    asyncio.run(leads._auto_score_lead("lead-123"))

        self.assertFalse(session.committed)
        self.assertTrue(session.rolled_back)


if __name__ == "__main__":
    unittest.main()
