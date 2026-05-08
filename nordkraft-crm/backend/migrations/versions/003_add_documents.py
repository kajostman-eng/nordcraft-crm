"""add documents

Revision ID: 003
Revises: 002
Create Date: 2026-05-08
"""

from alembic import op
import sqlalchemy as sa


revision = "003"
down_revision = "002"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "documents",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("title", sa.String(300), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("file_name", sa.String(500), nullable=False),
        sa.Column("content_type", sa.String(200)),
        sa.Column("size_bytes", sa.Integer()),
        sa.Column("storage_key", sa.String(800), nullable=False),
        sa.Column("url", sa.String(1000)),
        sa.Column("lead_id", sa.String(), sa.ForeignKey("leads.id"), nullable=True),
        sa.Column("client_id", sa.String(), sa.ForeignKey("clients.id"), nullable=True),
        sa.Column("uploaded_by", sa.String(), sa.ForeignKey("users.id"), nullable=True),
    )
    op.create_index("ix_documents_lead_id", "documents", ["lead_id"])
    op.create_index("ix_documents_client_id", "documents", ["client_id"])


def downgrade():
    op.drop_index("ix_documents_client_id", table_name="documents")
    op.drop_index("ix_documents_lead_id", table_name="documents")
    op.drop_table("documents")

