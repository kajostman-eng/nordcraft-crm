"""initial schema

Revision ID: 001
Revises:
Create Date: 2025-01-01 00:00:00
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "users",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("email", sa.String(255), unique=True, nullable=False),
        sa.Column("full_name", sa.String(200)),
        sa.Column("avatar_url", sa.String(500)),
        sa.Column("role", sa.String(50), server_default="member"),
        sa.Column("is_active", sa.Boolean(), server_default="true"),
        sa.Column("supabase_uid", sa.String(200), unique=True),
    )

    op.create_table(
        "leads",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("first_name", sa.String(100), nullable=False),
        sa.Column("last_name", sa.String(100), nullable=False),
        sa.Column("email", sa.String(255), unique=True, nullable=False),
        sa.Column("phone", sa.String(50)),
        sa.Column("linkedin_url", sa.String(500)),
        sa.Column("title", sa.String(200)),
        sa.Column("company_name", sa.String(200)),
        sa.Column("company_website", sa.String(500)),
        sa.Column("company_size", sa.String(50)),
        sa.Column("industry", sa.String(100)),
        sa.Column("country", sa.String(100)),
        sa.Column("city", sa.String(100)),
        sa.Column("status", sa.String(50), server_default="new"),
        sa.Column("source", sa.String(50), server_default="other"),
        sa.Column("assigned_to", sa.String(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("estimated_value", sa.Float(), server_default="0"),
        sa.Column("currency", sa.String(3), server_default="EUR"),
        sa.Column("notes", sa.Text()),
        sa.Column("ai_score", sa.Integer(), server_default="0"),
        sa.Column("automation_readiness", sa.Integer(), server_default="0"),
        sa.Column("ai_maturity_level", sa.Integer(), server_default="1"),
        sa.Column("estimated_time_savings_hrs", sa.Integer(), server_default="0"),
        sa.Column("estimated_roi_multiplier", sa.Float(), server_default="0"),
        sa.Column("ai_assessment_json", postgresql.JSON()),
        sa.Column("last_assessed_at", sa.DateTime()),
        sa.Column("enriched", sa.Boolean(), server_default="false"),
        sa.Column("enriched_at", sa.DateTime()),
        sa.Column("enrichment_data", postgresql.JSON()),
    )
    op.create_index("ix_leads_status", "leads", ["status"])
    op.create_index("ix_leads_ai_score", "leads", ["ai_score"])
    op.create_index("ix_leads_industry", "leads", ["industry"])

    op.create_table(
        "clients",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("lead_id", sa.String(), sa.ForeignKey("leads.id"), nullable=True),
        sa.Column("company_name", sa.String(200), nullable=False),
        sa.Column("industry", sa.String(100)),
        sa.Column("country", sa.String(100)),
        sa.Column("plan", sa.String(100)),
        sa.Column("mrr", sa.Float(), server_default="0"),
        sa.Column("contract_start", sa.DateTime()),
        sa.Column("contract_end", sa.DateTime()),
        sa.Column("currency", sa.String(3), server_default="EUR"),
        sa.Column("health_score", sa.Integer(), server_default="100"),
        sa.Column("health_status", sa.String(50), server_default="healthy"),
        sa.Column("slack_channel", sa.String(200)),
        sa.Column("notion_workspace_url", sa.String(500)),
        sa.Column("portal_url", sa.String(500)),
    )

    op.create_table(
        "client_contacts",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("client_id", sa.String(), sa.ForeignKey("clients.id"), nullable=False),
        sa.Column("name", sa.String(200)),
        sa.Column("email", sa.String(255)),
        sa.Column("title", sa.String(200)),
        sa.Column("is_primary", sa.Boolean(), server_default="false"),
    )

    op.create_table(
        "projects",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("client_id", sa.String(), sa.ForeignKey("clients.id"), nullable=False),
        sa.Column("name", sa.String(300), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("phase", sa.Integer(), server_default="1"),
        sa.Column("status", sa.String(50), server_default="active"),
        sa.Column("start_date", sa.DateTime()),
        sa.Column("target_end_date", sa.DateTime()),
        sa.Column("actual_end_date", sa.DateTime()),
        sa.Column("risk_level", sa.String(20), server_default="low"),
        sa.Column("risk_reason", sa.Text()),
    )

    op.create_table(
        "automations",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("client_id", sa.String(), sa.ForeignKey("clients.id"), nullable=True),
        sa.Column("name", sa.String(300), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("n8n_workflow_id", sa.String(200)),
        sa.Column("webhook_url", sa.String(500)),
        sa.Column("status", sa.String(50), server_default="draft"),
        sa.Column("total_runs", sa.Integer(), server_default="0"),
        sa.Column("last_run_at", sa.DateTime()),
        sa.Column("last_run_status", sa.String(50)),
        sa.Column("estimated_time_saved_per_run_minutes", sa.Integer(), server_default="0"),
    )

    op.create_table(
        "automation_runs",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("automation_id", sa.String(), sa.ForeignKey("automations.id"), nullable=False),
        sa.Column("started_at", sa.DateTime(), nullable=False),
        sa.Column("finished_at", sa.DateTime()),
        sa.Column("status", sa.String(50)),
        sa.Column("input_data", postgresql.JSON()),
        sa.Column("output_data", postgresql.JSON()),
        sa.Column("error_message", sa.Text()),
    )

    op.create_table(
        "tasks",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("lead_id", sa.String(), sa.ForeignKey("leads.id"), nullable=True),
        sa.Column("client_id", sa.String(), sa.ForeignKey("clients.id"), nullable=True),
        sa.Column("project_id", sa.String(), sa.ForeignKey("projects.id"), nullable=True),
        sa.Column("assigned_to", sa.String(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("due_date", sa.DateTime()),
        sa.Column("completed", sa.Boolean(), server_default="false"),
        sa.Column("completed_at", sa.DateTime()),
        sa.Column("priority", sa.String(20), server_default="medium"),
        sa.Column("source", sa.String(50), server_default="manual"),
    )

    op.create_table(
        "activities",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("lead_id", sa.String(), sa.ForeignKey("leads.id"), nullable=True),
        sa.Column("client_id", sa.String(), sa.ForeignKey("clients.id"), nullable=True),
        sa.Column("user_id", sa.String(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("type", sa.String(50)),
        sa.Column("title", sa.String(500)),
        sa.Column("body", sa.Text()),
        sa.Column("metadata", postgresql.JSON()),
    )

    op.create_table(
        "proposals",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("lead_id", sa.String(), sa.ForeignKey("leads.id"), nullable=False),
        sa.Column("generated_by_ai", sa.Boolean(), server_default="false"),
        sa.Column("status", sa.String(50), server_default="draft"),
        sa.Column("content_json", postgresql.JSON()),
        sa.Column("pdf_url", sa.String(500)),
        sa.Column("sent_at", sa.DateTime()),
        sa.Column("viewed_at", sa.DateTime()),
        sa.Column("responded_at", sa.DateTime()),
    )


def downgrade():
    for table in ["proposals", "activities", "tasks", "automation_runs",
                  "automations", "projects", "client_contacts", "clients", "leads", "users"]:
        op.drop_table(table)
