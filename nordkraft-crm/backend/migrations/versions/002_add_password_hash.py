"""add password_hash to users

Revision ID: 002
Revises: 001
Create Date: 2026-05-08
"""

from alembic import op
import sqlalchemy as sa


revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("users", sa.Column("password_hash", sa.String(255), nullable=True))


def downgrade():
    op.drop_column("users", "password_hash")

