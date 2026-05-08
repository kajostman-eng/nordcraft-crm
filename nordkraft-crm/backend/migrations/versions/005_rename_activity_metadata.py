"""rename activities.metadata to activity_meta_json

Avoids SQLAlchemy reserved name clashes; column was never 'metadata' as a Python attr reliably on all versions.

Revision ID: 005
Revises: 004
Create Date: 2026-05-09
"""

from alembic import op
from sqlalchemy.dialects import postgresql

revision = "005"
down_revision = "004"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column(
        "activities",
        "metadata",
        new_column_name="activity_meta_json",
        existing_type=postgresql.JSON(),
        existing_nullable=True,
    )


def downgrade():
    op.alter_column(
        "activities",
        "activity_meta_json",
        new_column_name="metadata",
        existing_type=postgresql.JSON(),
        existing_nullable=True,
    )
