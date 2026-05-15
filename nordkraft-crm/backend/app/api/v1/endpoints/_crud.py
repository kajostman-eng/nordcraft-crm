from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from app.db.session import get_db
from app.models.models import Client, Task, Automation
from app.schemas.schemas import ClientCreate, ClientOut, ClientUpdate, TaskCreate, TaskOut, AutomationCreate, AutomationOut
from datetime import datetime

# ─── Clients ──────────────────────────────────────────────────────────────────

clients_router = APIRouter()


@clients_router.get("/", response_model=List[ClientOut])
async def list_clients(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Client).order_by(Client.created_at.desc()))
    return result.scalars().all()


@clients_router.post("/", response_model=ClientOut, status_code=201)
async def create_client(payload: ClientCreate, db: AsyncSession = Depends(get_db)):
    client = Client(**payload.model_dump())
    db.add(client)
    await db.commit()
    await db.refresh(client)
    return client


@clients_router.get("/{client_id}", response_model=ClientOut)
async def get_client(client_id: str, db: AsyncSession = Depends(get_db)):
    client = await db.get(Client, client_id)
    if not client:
        raise HTTPException(404, "Client not found")
    return client


@clients_router.patch("/{client_id}", response_model=ClientOut)
async def update_client(client_id: str, payload: ClientUpdate, db: AsyncSession = Depends(get_db)):
    client = await db.get(Client, client_id)
    if not client:
        raise HTTPException(404, "Client not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(client, k, v)
    client.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(client)
    return client


# ─── Tasks ────────────────────────────────────────────────────────────────────

tasks_router = APIRouter()


@tasks_router.get("/", response_model=List[TaskOut])
async def list_tasks(
    lead_id: str = None,
    client_id: str = None,
    completed: bool = None,
    db: AsyncSession = Depends(get_db),
):
    q = select(Task)
    if lead_id:
        q = q.where(Task.lead_id == lead_id)
    if client_id:
        q = q.where(Task.client_id == client_id)
    if completed is not None:
        q = q.where(Task.completed == completed)
    q = q.order_by(Task.due_date.asc().nulls_last(), Task.created_at.desc())
    result = await db.execute(q)
    return result.scalars().all()


@tasks_router.post("/", response_model=TaskOut, status_code=201)
async def create_task(payload: TaskCreate, db: AsyncSession = Depends(get_db)):
    task = Task(**payload.model_dump())
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return task


@tasks_router.patch("/{task_id}/complete", response_model=TaskOut)
async def complete_task(task_id: str, db: AsyncSession = Depends(get_db)):
    task = await db.get(Task, task_id)
    if not task:
        raise HTTPException(404, "Task not found")
    task.completed = True
    task.completed_at = datetime.utcnow()
    await db.commit()
    await db.refresh(task)
    return task


# ─── Automations ──────────────────────────────────────────────────────────────

automations_router = APIRouter()


@automations_router.get("/", response_model=List[AutomationOut])
async def list_automations(client_id: str = None, db: AsyncSession = Depends(get_db)):
    q = select(Automation)
    if client_id:
        q = q.where(Automation.client_id == client_id)
    q = q.order_by(Automation.total_runs.desc())
    result = await db.execute(q)
    return result.scalars().all()


@automations_router.post("/", response_model=AutomationOut, status_code=201)
async def create_automation(payload: AutomationCreate, db: AsyncSession = Depends(get_db)):
    auto = Automation(**payload.model_dump())
    db.add(auto)
    await db.commit()
    await db.refresh(auto)
    return auto


@automations_router.patch("/{auto_id}/toggle", response_model=AutomationOut)
async def toggle_automation(auto_id: str, db: AsyncSession = Depends(get_db)):
    auto = await db.get(Automation, auto_id)
    if not auto:
        raise HTTPException(404, "Automation not found")
    auto.status = "paused" if auto.status == "active" else "active"
    auto.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(auto)
    return auto
