from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import AsyncSessionLocal
from app.models.models import Lead
from app.services.ai_service import run_ai_assessment


def apply_assessment_to_lead(lead: Lead, assessment: dict) -> None:
    lead.ai_score = assessment["ai_score"]
    lead.automation_readiness = assessment["automation_readiness"]
    lead.ai_maturity_level = assessment["ai_maturity_level"]
    lead.estimated_time_savings_hrs = assessment["estimated_time_savings_hrs"]
    lead.estimated_roi_multiplier = assessment["estimated_roi_multiplier"]
    lead.ai_assessment_json = assessment
    lead.last_assessed_at = datetime.utcnow()


async def assess_and_persist_lead(
    db: AsyncSession,
    lead: Lead,
    context_notes: str = "",
) -> dict:
    assessment = await run_ai_assessment(lead, context_notes)
    apply_assessment_to_lead(lead, assessment)
    await db.commit()
    return assessment


async def auto_score_lead(lead_id: str) -> None:
    async with AsyncSessionLocal() as db:
        try:
            lead = await db.get(Lead, lead_id)
            if not lead:
                return
            await assess_and_persist_lead(db, lead)
        except Exception:
            await db.rollback()
