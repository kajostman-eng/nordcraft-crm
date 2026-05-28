from collections.abc import Awaitable, Callable
from datetime import datetime
from typing import Any


AssessmentRunner = Callable[[Any, str], Awaitable[dict[str, Any]]]


def apply_assessment_to_lead(
    lead: Any,
    assessment: dict[str, Any],
    assessed_at: datetime | None = None,
) -> None:
    lead.ai_score = assessment["ai_score"]
    lead.automation_readiness = assessment["automation_readiness"]
    lead.ai_maturity_level = assessment["ai_maturity_level"]
    lead.estimated_time_savings_hrs = assessment["estimated_time_savings_hrs"]
    lead.estimated_roi_multiplier = assessment["estimated_roi_multiplier"]
    lead.ai_assessment_json = assessment
    lead.last_assessed_at = assessed_at or datetime.utcnow()


async def assess_and_persist_lead(
    db: Any,
    lead: Any,
    context_notes: str = "",
    runner: AssessmentRunner | None = None,
) -> dict[str, Any]:
    if runner is None:
        from app.services.ai_service import run_ai_assessment

        runner = run_ai_assessment

    assessment = await runner(lead, context_notes or "")
    apply_assessment_to_lead(lead, assessment)
    await db.commit()
    return assessment
