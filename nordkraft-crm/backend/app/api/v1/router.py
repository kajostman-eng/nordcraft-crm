from fastapi import APIRouter
from app.api.v1.endpoints import leads, clients, tasks, automations, dashboard, ai

api_router = APIRouter()

api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
api_router.include_router(leads.router, prefix="/leads", tags=["Leads"])
api_router.include_router(clients.router, prefix="/clients", tags=["Clients"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["Tasks"])
api_router.include_router(automations.router, prefix="/automations", tags=["Automations"])
api_router.include_router(ai.router, prefix="/ai", tags=["AI"])
