from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Text, ForeignKey, Enum as SAEnum, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import uuid
import enum

Base = declarative_base()


def gen_uuid():
    return str(uuid.uuid4())


class LeadStatus(str, enum.Enum):
    new = "new"
    contacted = "contacted"
    qualified = "qualified"
    discovery_booked = "discovery_booked"
    proposal_sent = "proposal_sent"
    negotiation = "negotiation"
    won = "won"
    lost = "lost"
    onboarding = "onboarding"


class LeadSource(str, enum.Enum):
    linkedin = "linkedin"
    cold_email = "cold_email"
    referral = "referral"
    website = "website"
    event = "event"
    other = "other"


class AutomationStatus(str, enum.Enum):
    active = "active"
    paused = "paused"
    error = "error"
    draft = "draft"


class ClientHealthStatus(str, enum.Enum):
    healthy = "healthy"
    at_risk = "at_risk"
    churning = "churning"


# ─── Lead ────────────────────────────────────────────────────────────────────

class Lead(Base):
    __tablename__ = "leads"

    id = Column(String, primary_key=True, default=gen_uuid)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Identity
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    phone = Column(String(50))
    linkedin_url = Column(String(500))
    title = Column(String(200))

    # Company
    company_name = Column(String(200))
    company_website = Column(String(500))
    company_size = Column(String(50))
    industry = Column(String(100))
    country = Column(String(100))
    city = Column(String(100))

    # CRM
    status = Column(SAEnum(LeadStatus), default=LeadStatus.new)
    source = Column(SAEnum(LeadSource), default=LeadSource.other)
    assigned_to = Column(String, ForeignKey("users.id"), nullable=True)
    estimated_value = Column(Float, default=0.0)
    currency = Column(String(3), default="EUR")
    notes = Column(Text)

    # AI Assessment
    ai_score = Column(Integer, default=0)            # 0-100
    automation_readiness = Column(Integer, default=0) # 0-100
    ai_maturity_level = Column(Integer, default=1)   # 1-5
    estimated_time_savings_hrs = Column(Integer, default=0)
    estimated_roi_multiplier = Column(Float, default=0.0)
    ai_assessment_json = Column(JSON)                 # full structured assessment
    last_assessed_at = Column(DateTime)

    # Enrichment
    enriched = Column(Boolean, default=False)
    enriched_at = Column(DateTime)
    enrichment_data = Column(JSON)

    # Relations
    activities = relationship("Activity", back_populates="lead", cascade="all, delete")
    tasks = relationship("Task", back_populates="lead", cascade="all, delete")
    proposals = relationship("Proposal", back_populates="lead", cascade="all, delete")
    assigned_user = relationship("User", foreign_keys=[assigned_to])


# ─── Client (converted lead) ─────────────────────────────────────────────────

class Client(Base):
    __tablename__ = "clients"

    id = Column(String, primary_key=True, default=gen_uuid)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    lead_id = Column(String, ForeignKey("leads.id"), nullable=True)
    company_name = Column(String(200), nullable=False)
    industry = Column(String(100))
    country = Column(String(100))

    # Contract
    plan = Column(String(100))          # growth, enterprise, etc.
    mrr = Column(Float, default=0.0)
    contract_start = Column(DateTime)
    contract_end = Column(DateTime)
    currency = Column(String(3), default="EUR")

    # Health
    health_score = Column(Integer, default=100)
    health_status = Column(SAEnum(ClientHealthStatus), default=ClientHealthStatus.healthy)

    # Workspace metadata
    slack_channel = Column(String(200))
    notion_workspace_url = Column(String(500))
    portal_url = Column(String(500))

    # Relations
    projects = relationship("Project", back_populates="client", cascade="all, delete")
    automations = relationship("Automation", back_populates="client", cascade="all, delete")
    tasks = relationship("Task", back_populates="client", cascade="all, delete")
    contacts = relationship("ClientContact", back_populates="client", cascade="all, delete")


class ClientContact(Base):
    __tablename__ = "client_contacts"

    id = Column(String, primary_key=True, default=gen_uuid)
    client_id = Column(String, ForeignKey("clients.id"), nullable=False)
    name = Column(String(200))
    email = Column(String(255))
    title = Column(String(200))
    is_primary = Column(Boolean, default=False)

    client = relationship("Client", back_populates="contacts")


# ─── Project ─────────────────────────────────────────────────────────────────

class Project(Base):
    __tablename__ = "projects"

    id = Column(String, primary_key=True, default=gen_uuid)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    client_id = Column(String, ForeignKey("clients.id"), nullable=False)
    name = Column(String(300), nullable=False)
    description = Column(Text)
    phase = Column(Integer, default=1)    # 1, 2, 3
    status = Column(String(50), default="active")
    start_date = Column(DateTime)
    target_end_date = Column(DateTime)
    actual_end_date = Column(DateTime)

    # AI risk detection
    risk_level = Column(String(20), default="low")   # low, medium, high
    risk_reason = Column(Text)

    client = relationship("Client", back_populates="projects")
    tasks = relationship("Task", back_populates="project", cascade="all, delete")


# ─── Automation ───────────────────────────────────────────────────────────────

class Automation(Base):
    __tablename__ = "automations"

    id = Column(String, primary_key=True, default=gen_uuid)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    client_id = Column(String, ForeignKey("clients.id"), nullable=True)  # null = internal
    name = Column(String(300), nullable=False)
    description = Column(Text)
    n8n_workflow_id = Column(String(200))
    webhook_url = Column(String(500))
    status = Column(SAEnum(AutomationStatus), default=AutomationStatus.draft)

    # Stats
    total_runs = Column(Integer, default=0)
    last_run_at = Column(DateTime)
    last_run_status = Column(String(50))
    estimated_time_saved_per_run_minutes = Column(Integer, default=0)

    client = relationship("Client", back_populates="automations")
    runs = relationship("AutomationRun", back_populates="automation", cascade="all, delete")


class AutomationRun(Base):
    __tablename__ = "automation_runs"

    id = Column(String, primary_key=True, default=gen_uuid)
    automation_id = Column(String, ForeignKey("automations.id"), nullable=False)
    started_at = Column(DateTime, default=datetime.utcnow)
    finished_at = Column(DateTime)
    status = Column(String(50))   # success, error, running
    input_data = Column(JSON)
    output_data = Column(JSON)
    error_message = Column(Text)

    automation = relationship("Automation", back_populates="runs")


# ─── Task ─────────────────────────────────────────────────────────────────────

class Task(Base):
    __tablename__ = "tasks"

    id = Column(String, primary_key=True, default=gen_uuid)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    lead_id = Column(String, ForeignKey("leads.id"), nullable=True)
    client_id = Column(String, ForeignKey("clients.id"), nullable=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=True)
    assigned_to = Column(String, ForeignKey("users.id"), nullable=True)

    title = Column(String(500), nullable=False)
    description = Column(Text)
    due_date = Column(DateTime)
    completed = Column(Boolean, default=False)
    completed_at = Column(DateTime)
    priority = Column(String(20), default="medium")   # low, medium, high, urgent
    source = Column(String(50), default="manual")     # manual, ai_extracted, automation

    lead = relationship("Lead", back_populates="tasks")
    client = relationship("Client", back_populates="tasks")
    project = relationship("Project", back_populates="tasks")
    assigned_user = relationship("User", foreign_keys=[assigned_to])


# ─── Activity ─────────────────────────────────────────────────────────────────

class Activity(Base):
    __tablename__ = "activities"

    id = Column(String, primary_key=True, default=gen_uuid)
    created_at = Column(DateTime, default=datetime.utcnow)

    lead_id = Column(String, ForeignKey("leads.id"), nullable=True)
    client_id = Column(String, ForeignKey("clients.id"), nullable=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=True)

    type = Column(String(50))    # call, email, meeting, note, proposal, ai_action
    title = Column(String(500))
    body = Column(Text)
    metadata = Column(JSON)

    lead = relationship("Lead", back_populates="activities")


# ─── Proposal ─────────────────────────────────────────────────────────────────

class Proposal(Base):
    __tablename__ = "proposals"

    id = Column(String, primary_key=True, default=gen_uuid)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    lead_id = Column(String, ForeignKey("leads.id"), nullable=False)
    generated_by_ai = Column(Boolean, default=False)
    status = Column(String(50), default="draft")   # draft, sent, viewed, accepted, rejected
    content_json = Column(JSON)
    pdf_url = Column(String(500))
    sent_at = Column(DateTime)
    viewed_at = Column(DateTime)
    responded_at = Column(DateTime)

    lead = relationship("Lead", back_populates="proposals")


# ─── User ─────────────────────────────────────────────────────────────────────

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=gen_uuid)
    created_at = Column(DateTime, default=datetime.utcnow)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=True)
    full_name = Column(String(200))
    avatar_url = Column(String(500))
    role = Column(String(50), default="member")    # admin, member, viewer
    is_active = Column(Boolean, default=True)
    supabase_uid = Column(String(200), unique=True)
