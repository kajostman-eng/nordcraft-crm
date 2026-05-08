from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.models.models import Lead, Client
from app.schemas.schemas import (
    AIAssessmentRequest, AIProposalRequest,
    AIFollowUpRequest, AIChatRequest,
)
from app.services.ai_service import (
    run_ai_assessment, generate_proposal,
    generate_follow_up_email, summarise_meeting, ai_chat,
)
from pydantic import BaseModel
from typing import Optional

router = APIRouter()


@router.post("/assess")
async def assess(payload: AIAssessmentRequest, db: AsyncSession = Depends(get_db)):
    lead = await db.get(Lead, payload.lead_id)
    if not lead:
        raise HTTPException(404, "Lead not found")
    result = await run_ai_assessment(lead, payload.context_notes or "")
    return result


@router.post("/proposal")
async def proposal(payload: AIProposalRequest, db: AsyncSession = Depends(get_db)):
    lead = await db.get(Lead, payload.lead_id)
    if not lead:
        raise HTTPException(404, "Lead not found")
    assessment = lead.ai_assessment_json or {}
    result = await generate_proposal(lead, assessment, payload.tone)
    return result


@router.post("/follow-up")
async def follow_up(payload: AIFollowUpRequest, db: AsyncSession = Depends(get_db)):
    lead = await db.get(Lead, payload.lead_id)
    if not lead:
        raise HTTPException(404, "Lead not found")
    result = await generate_follow_up_email(lead, payload.context or "", payload.tone)
    return result


class MeetingRequest(BaseModel):
    transcript: str
    lead_id: Optional[str] = None
    client_id: Optional[str] = None
    participant_name: Optional[str] = "Client"


@router.post("/meeting-summary")
async def meeting_summary(payload: MeetingRequest, db: AsyncSession = Depends(get_db)):
    name = payload.participant_name
    if payload.lead_id:
        lead = await db.get(Lead, payload.lead_id)
        if lead:
            name = f"{lead.first_name} {lead.last_name} at {lead.company_name}"
    elif payload.client_id:
        client = await db.get(Client, payload.client_id)
        if client:
            name = client.company_name
    result = await summarise_meeting(payload.transcript, name)
    return result


@router.post("/chat")
async def chat(payload: AIChatRequest, db: AsyncSession = Depends(get_db)):
    context_data = {}
    if payload.context_id and payload.context_type == "lead":
        lead = await db.get(Lead, payload.context_id)
        if lead:
            context_data = {
                "name": f"{lead.first_name} {lead.last_name}",
                "company": lead.company_name,
                "status": lead.status,
                "ai_score": lead.ai_score,
                "industry": lead.industry,
            }
    elif payload.context_id and payload.context_type == "client":
        client = await db.get(Client, payload.context_id)
        if client:
            context_data = {
                "company": client.company_name,
                "plan": client.plan,
                "mrr": client.mrr,
                "health_score": client.health_score,
            }

    reply = await ai_chat(
        payload.message,
        payload.history or [],
        payload.context_type,
        context_data,
    )
    return {"reply": reply}
