from fastapi import APIRouter, Depends
from app.api.deps import get_current_user
from app.api.v1.endpoints import auth, leads, clients, tasks, automations, dashboard, ai

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])

protected = {"dependencies": [Depends(get_current_user)]}
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"], **protected)
api_router.include_router(leads.router, prefix="/leads", tags=["Leads"], **protected)
api_router.include_router(clients.router, prefix="/clients", tags=["Clients"], **protected)
api_router.include_router(tasks.router, prefix="/tasks", tags=["Tasks"], **protected)
api_router.include_router(automations.router, prefix="/automations", tags=["Automations"], **protected)
api_router.include_router(ai.router, prefix="/ai", tags=["AI"], **protected)
