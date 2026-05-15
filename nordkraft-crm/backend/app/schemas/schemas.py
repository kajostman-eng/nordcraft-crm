from pydantic import BaseModel, EmailStr
from typing import Optional, List, Any
from datetime import datetime
from enum import Enum


# ─── Enums ────────────────────────────────────────────────────────────────────

class LeadStatus(str, Enum):
    new = "new"
    contacted = "contacted"
    qualified = "qualified"
    discovery_booked = "discovery_booked"
    proposal_sent = "proposal_sent"
    negotiation = "negotiation"
    won = "won"
    lost = "lost"
    onboarding = "onboarding"


class LeadSource(str, Enum):
    linkedin = "linkedin"
    cold_email = "cold_email"
    referral = "referral"
    website = "website"
    event = "event"
    other = "other"


# ─── Lead Schemas ─────────────────────────────────────────────────────────────

class LeadCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: Optional[str] = None
    linkedin_url: Optional[str] = None
    title: Optional[str] = None
    company_name: Optional[str] = None
    company_website: Optional[str] = None
    company_size: Optional[str] = None
    industry: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    source: LeadSource = LeadSource.other
    estimated_value: float = 0.0
    notes: Optional[str] = None


class LeadUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    title: Optional[str] = None
    company_name: Optional[str] = None
    industry: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    status: Optional[LeadStatus] = None
    estimated_value: Optional[float] = None
    notes: Optional[str] = None
    assigned_to: Optional[str] = None


class AIAssessment(BaseModel):
    ai_score: int
    automation_readiness: int
    ai_maturity_level: int
    estimated_time_savings_hrs: int
    estimated_roi_multiplier: float
    key_opportunities: List[str]
    recommended_phases: List[dict]
    summary: str


class LeadOut(BaseModel):
    id: str
    created_at: datetime
    first_name: str
    last_name: str
    email: str
    phone: Optional[str]
    linkedin_url: Optional[str]
    title: Optional[str]
    company_name: Optional[str]
    company_website: Optional[str]
    industry: Optional[str]
    country: Optional[str]
    city: Optional[str]
    status: LeadStatus
    source: LeadSource
    estimated_value: float
    currency: str
    notes: Optional[str]
    ai_score: int
    automation_readiness: int
    ai_maturity_level: int
    estimated_time_savings_hrs: int
    estimated_roi_multiplier: float
    enriched: bool
    assigned_to: Optional[str]

    class Config:
        from_attributes = True


# ─── Client Schemas ───────────────────────────────────────────────────────────

class ClientCreate(BaseModel):
    lead_id: Optional[str] = None
    company_name: str
    industry: Optional[str] = None
    country: Optional[str] = None
    plan: Optional[str] = None
    mrr: float = 0.0
    contract_start: Optional[datetime] = None
    contract_end: Optional[datetime] = None


class ClientUpdate(BaseModel):
    lead_id: Optional[str] = None
    company_name: Optional[str] = None
    industry: Optional[str] = None
    country: Optional[str] = None
    plan: Optional[str] = None
    mrr: Optional[float] = None
    contract_start: Optional[datetime] = None
    contract_end: Optional[datetime] = None
    currency: Optional[str] = None
    health_score: Optional[int] = None
    health_status: Optional[str] = None
    slack_channel: Optional[str] = None
    notion_workspace_url: Optional[str] = None
    portal_url: Optional[str] = None


class ClientOut(BaseModel):
    id: str
    created_at: datetime
    company_name: str
    industry: Optional[str]
    country: Optional[str]
    plan: Optional[str]
    mrr: float
    currency: str
    health_score: int
    health_status: str
    contract_start: Optional[datetime]
    contract_end: Optional[datetime]
    portal_url: Optional[str]

    class Config:
        from_attributes = True


# ─── Task Schemas ─────────────────────────────────────────────────────────────

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    priority: str = "medium"
    lead_id: Optional[str] = None
    client_id: Optional[str] = None
    project_id: Optional[str] = None
    assigned_to: Optional[str] = None


class TaskOut(BaseModel):
    id: str
    created_at: datetime
    title: str
    description: Optional[str]
    due_date: Optional[datetime]
    completed: bool
    priority: str
    source: str
    lead_id: Optional[str]
    client_id: Optional[str]
    project_id: Optional[str]
    assigned_to: Optional[str]

    class Config:
        from_attributes = True


# ─── Automation Schemas ───────────────────────────────────────────────────────

class AutomationCreate(BaseModel):
    client_id: Optional[str] = None
    name: str
    description: Optional[str] = None
    n8n_workflow_id: Optional[str] = None
    webhook_url: Optional[str] = None
    estimated_time_saved_per_run_minutes: int = 0


class AutomationOut(BaseModel):
    id: str
    created_at: datetime
    client_id: Optional[str]
    name: str
    description: Optional[str]
    status: str
    total_runs: int
    last_run_at: Optional[datetime]
    last_run_status: Optional[str]
    estimated_time_saved_per_run_minutes: int

    class Config:
        from_attributes = True


# ─── Activity Schemas ─────────────────────────────────────────────────────────

class ActivityOut(BaseModel):
    id: str
    created_at: datetime
    activity_kind: str
    title: str
    body: Optional[str]
    lead_id: Optional[str]
    client_id: Optional[str]
    user_id: Optional[str]

    class Config:
        from_attributes = True


# ─── Proposal Schemas ─────────────────────────────────────────────────────────

class ProposalOut(BaseModel):
    id: str
    created_at: datetime
    lead_id: str
    generated_by_ai: bool
    status: str
    content_json: Optional[Any]
    pdf_url: Optional[str]
    sent_at: Optional[datetime]

    class Config:
        from_attributes = True


# ─── Dashboard ────────────────────────────────────────────────────────────────

class DashboardStats(BaseModel):
    pipeline_value_eur: float
    active_leads: int
    active_clients: int
    live_automations: int
    automation_runs_today: int
    hours_saved_this_month: float
    new_leads_this_week: int
    renewals_due_soon: int


# ─── AI Endpoints ─────────────────────────────────────────────────────────────

class AIAssessmentRequest(BaseModel):
    lead_id: str
    context_notes: Optional[str] = None


class AIProposalRequest(BaseModel):
    lead_id: str
    assessment_id: Optional[str] = None
    tone: str = "professional"


class AIFollowUpRequest(BaseModel):
    lead_id: str
    context: Optional[str] = None
    tone: str = "friendly_professional"


class AIChatRequest(BaseModel):
    message: str
    context_type: str = "general"   # general, lead, client, project
    context_id: Optional[str] = None
    history: Optional[List[dict]] = []


# ─── Auth ──────────────────────────────────────────────────────────────────────

class AuthLoginRequest(BaseModel):
    email: EmailStr
    password: str


class AuthToken(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    id: str
    created_at: datetime
    email: EmailStr
    full_name: Optional[str]
    avatar_url: Optional[str]
    role: str
    is_active: bool

    class Config:
        from_attributes = True


class BootstrapAdminRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None


# ─── Documents ────────────────────────────────────────────────────────────────

class DocumentOut(BaseModel):
    id: str
    created_at: datetime
    updated_at: datetime
    title: str
    description: Optional[str]
    file_name: str
    content_type: Optional[str]
    size_bytes: Optional[int]
    storage_key: str
    url: Optional[str]
    lead_id: Optional[str]
    client_id: Optional[str]
    uploaded_by: Optional[str]

    class Config:
        from_attributes = True


# ─── Products / Offers ────────────────────────────────────────────────────────

class ProductCreate(BaseModel):
    name: str
    description: Optional[str] = None
    sku: Optional[str] = None
    unit_price: float = 0.0
    currency: str = "EUR"
    is_active: bool = True
    tags: Optional[str] = None


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    sku: Optional[str] = None
    unit_price: Optional[float] = None
    currency: Optional[str] = None
    is_active: Optional[bool] = None
    tags: Optional[str] = None


class ProductOut(BaseModel):
    id: str
    created_at: datetime
    updated_at: datetime
    name: str
    description: Optional[str]
    sku: Optional[str]
    unit_price: float
    currency: str
    is_active: bool
    tags: Optional[str]

    class Config:
        from_attributes = True


class OfferCreate(BaseModel):
    title: str
    lead_id: Optional[str] = None
    client_id: Optional[str] = None
    currency: str = "EUR"
    notes: Optional[str] = None
    discount_amount: float = 0.0


class OfferUpdate(BaseModel):
    title: Optional[str] = None
    status: Optional[str] = None
    currency: Optional[str] = None
    lead_id: Optional[str] = None
    client_id: Optional[str] = None
    notes: Optional[str] = None
    discount_amount: Optional[float] = None


class OfferOut(BaseModel):
    id: str
    created_at: datetime
    updated_at: datetime
    title: str
    status: str
    currency: str
    lead_id: Optional[str]
    client_id: Optional[str]
    created_by: Optional[str]
    notes: Optional[str]
    discount_amount: float

    class Config:
        from_attributes = True


class OfferItemCreate(BaseModel):
    product_id: str
    quantity: int = 1
    unit_price: Optional[float] = None
    description: Optional[str] = None


class OfferItemUpdate(BaseModel):
    quantity: Optional[int] = None
    unit_price: Optional[float] = None
    description: Optional[str] = None


class OfferItemOut(BaseModel):
    id: str
    offer_id: str
    product_id: str
    quantity: int
    unit_price: float
    line_total: float
    description: Optional[str]

    class Config:
        from_attributes = True
