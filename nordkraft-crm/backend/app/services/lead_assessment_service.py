from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import Lead
from app.services.ai_service import run_ai_assessment


async def run_and_persist_ai_assessment(
    lead: Lead,
    db: AsyncSession,
    context_notes: str = "",
) -> dict:
    assessment = await run_ai_assessment(lead, context_notes or "")

    lead.ai_score = assessment["ai_score"]
    lead.automation_readiness = assessment["automation_readiness"]
    lead.ai_maturity_level = assessment["ai_maturity_level"]
    lead.estimated_time_savings_hrs = assessment["estimated_time_savings_hrs"]
    lead.estimated_roi_multiplier = assessment["estimated_roi_multiplier"]
    lead.ai_assessment_json = assessment
    lead.last_assessed_at = datetime.utcnow()
    await db.commit()

    return assessment
