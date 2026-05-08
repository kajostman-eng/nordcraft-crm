from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from app.db.session import get_db
from app.models.models import Lead, Client, Task, Automation, AutomationRun
from app.schemas.schemas import DashboardStats
from datetime import datetime, timedelta

router = APIRouter()


@router.get("/stats", response_model=DashboardStats)
async def get_stats(db: AsyncSession = Depends(get_db)):
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    week_ago = datetime.utcnow() - timedelta(days=7)
    month_ago = datetime.utcnow() - timedelta(days=30)
    thirty_days_out = datetime.utcnow() + timedelta(days=30)

    pipeline_statuses = ["new", "contacted", "qualified", "discovery_booked", "proposal_sent", "negotiation"]

    pipeline_val = await db.execute(
        select(func.sum(Lead.estimated_value)).where(Lead.status.in_(pipeline_statuses))
    )
    pipeline_value = pipeline_val.scalar() or 0.0

    active_leads = await db.execute(
        select(func.count(Lead.id)).where(Lead.status.in_(pipeline_statuses))
    )

    active_clients = await db.execute(
        select(func.count(Client.id))
    )

    live_automations = await db.execute(
        select(func.count(Automation.id)).where(Automation.status == "active")
    )

    runs_today = await db.execute(
        select(func.count(AutomationRun.id)).where(AutomationRun.started_at >= today_start)
    )

    new_this_week = await db.execute(
        select(func.count(Lead.id)).where(Lead.created_at >= week_ago)
    )

    renewals_soon = await db.execute(
        select(func.count(Client.id)).where(
            and_(Client.contract_end >= datetime.utcnow(), Client.contract_end <= thirty_days_out)
        )
    )

    # Estimate hours saved: sum of (runs in month * minutes per run) / 60
    hours_result = await db.execute(
        select(
            func.sum(Automation.total_runs * Automation.estimated_time_saved_per_run_minutes)
        ).where(Automation.status == "active")
    )
    total_minutes = hours_result.scalar() or 0
    hours_saved = total_minutes / 60

    return DashboardStats(
        pipeline_value_eur=pipeline_value,
        active_leads=active_leads.scalar() or 0,
        active_clients=active_clients.scalar() or 0,
        live_automations=live_automations.scalar() or 0,
        automation_runs_today=runs_today.scalar() or 0,
        hours_saved_this_month=round(hours_saved, 1),
        new_leads_this_week=new_this_week.scalar() or 0,
        renewals_due_soon=renewals_soon.scalar() or 0,
    )
