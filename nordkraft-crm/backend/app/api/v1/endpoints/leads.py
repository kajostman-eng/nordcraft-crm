from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from typing import List, Optional
from app.db.session import get_db
from app.models.models import Lead, Activity
from app.schemas.schemas import LeadCreate, LeadUpdate, LeadOut, AIAssessmentRequest
from app.services.ai_service import run_ai_assessment
from datetime import datetime

router = APIRouter()


@router.get("/", response_model=List[LeadOut])
async def list_leads(
    status: Optional[str] = Query(None),
    source: Optional[str] = Query(None),
    industry: Optional[str] = Query(None),
    min_score: Optional[int] = Query(None),
    search: Optional[str] = Query(None),
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
):
    q = select(Lead)
    filters = []
    if status:
        filters.append(Lead.status == status)
    if source:
        filters.append(Lead.source == source)
    if industry:
        filters.append(Lead.industry.ilike(f"%{industry}%"))
    if min_score is not None:
        filters.append(Lead.ai_score >= min_score)
    if search:
        term = f"%{search}%"
        filters.append(
            (Lead.first_name.ilike(term))
            | (Lead.last_name.ilike(term))
            | (Lead.company_name.ilike(term))
            | (Lead.email.ilike(term))
        )
    if filters:
        q = q.where(and_(*filters))
    q = q.order_by(Lead.ai_score.desc()).offset(skip).limit(limit)
    result = await db.execute(q)
    return result.scalars().all()


@router.post("/", response_model=LeadOut, status_code=201)
async def create_lead(
    payload: LeadCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    lead = Lead(**payload.model_dump())
    db.add(lead)
    await db.commit()
    await db.refresh(lead)

    # Log activity
    activity = Activity(
        lead_id=lead.id,
        activity_kind="note",
        title=f"Lead created from {lead.source}",
    )
    db.add(activity)
    await db.commit()

    # Kick off async AI scoring
    background_tasks.add_task(_auto_score_lead, lead.id, db)

    return lead


@router.get("/{lead_id}", response_model=LeadOut)
async def get_lead(lead_id: str, db: AsyncSession = Depends(get_db)):
    lead = await db.get(Lead, lead_id)
    if not lead:
        raise HTTPException(404, "Lead not found")
    return lead


@router.patch("/{lead_id}", response_model=LeadOut)
async def update_lead(
    lead_id: str,
    payload: LeadUpdate,
    db: AsyncSession = Depends(get_db),
):
    lead = await db.get(Lead, lead_id)
    if not lead:
        raise HTTPException(404, "Lead not found")
    for field, val in payload.model_dump(exclude_unset=True).items():
        setattr(lead, field, val)
    lead.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(lead)
    return lead


@router.delete("/{lead_id}", status_code=204)
async def delete_lead(lead_id: str, db: AsyncSession = Depends(get_db)):
    lead = await db.get(Lead, lead_id)
    if not lead:
        raise HTTPException(404, "Lead not found")
    await db.delete(lead)
    await db.commit()


@router.post("/{lead_id}/assess")
async def assess_lead(
    lead_id: str,
    payload: AIAssessmentRequest,
    db: AsyncSession = Depends(get_db),
):
    """Run AI opportunity assessment on a lead."""
    lead = await db.get(Lead, lead_id)
    if not lead:
        raise HTTPException(404, "Lead not found")

    assessment = await run_ai_assessment(lead, payload.context_notes or "")

    # Persist scores
    lead.ai_score = assessment["ai_score"]
    lead.automation_readiness = assessment["automation_readiness"]
    lead.ai_maturity_level = assessment["ai_maturity_level"]
    lead.estimated_time_savings_hrs = assessment["estimated_time_savings_hrs"]
    lead.estimated_roi_multiplier = assessment["estimated_roi_multiplier"]
    lead.ai_assessment_json = assessment
    lead.last_assessed_at = datetime.utcnow()
    await db.commit()

    return assessment


@router.post("/{lead_id}/move")
async def move_pipeline_stage(
    lead_id: str,
    new_status: str,
    db: AsyncSession = Depends(get_db),
):
    lead = await db.get(Lead, lead_id)
    if not lead:
        raise HTTPException(404, "Lead not found")
    old = lead.status
    lead.status = new_status
    lead.updated_at = datetime.utcnow()

    activity = Activity(
        lead_id=lead.id,
        activity_kind="note",
        title=f"Stage changed: {old} → {new_status}",
    )
    db.add(activity)
    await db.commit()
    return {"status": new_status}


# ─── Background helpers ───────────────────────────────────────────────────────

async def _auto_score_lead(lead_id: str, db: AsyncSession):
    lead = await db.get(Lead, lead_id)
    if not lead:
        return
    try:
        assessment = await run_ai_assessment(lead)
        lead.ai_score = assessment["ai_score"]
        lead.automation_readiness = assessment["automation_readiness"]
        lead.ai_maturity_level = assessment["ai_maturity_level"]
        lead.estimated_time_savings_hrs = assessment["estimated_time_savings_hrs"]
        lead.estimated_roi_multiplier = assessment["estimated_roi_multiplier"]
        lead.ai_assessment_json = assessment
        lead.last_assessed_at = datetime.utcnow()
        await db.commit()
    except Exception:
        pass
