"""add products and offers

Revision ID: 004
Revises: 003
Create Date: 2026-05-08
"""

from alembic import op
import sqlalchemy as sa


revision = "004"
down_revision = "003"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "products",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("name", sa.String(300), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("sku", sa.String(120), unique=True),
        sa.Column("unit_price", sa.Float(), server_default="0"),
        sa.Column("currency", sa.String(3), server_default="EUR"),
        sa.Column("is_active", sa.Boolean(), server_default="true"),
        sa.Column("tags", sa.Text()),
    )
    op.create_index("ix_products_name", "products", ["name"])
    op.create_index("ix_products_active", "products", ["is_active"])

    op.create_table(
        "offers",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("title", sa.String(300), nullable=False),
        sa.Column("status", sa.String(50), server_default="draft"),
        sa.Column("currency", sa.String(3), server_default="EUR"),
        sa.Column("lead_id", sa.String(), sa.ForeignKey("leads.id"), nullable=True),
        sa.Column("client_id", sa.String(), sa.ForeignKey("clients.id"), nullable=True),
        sa.Column("created_by", sa.String(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("notes", sa.Text()),
        sa.Column("discount_amount", sa.Float(), server_default="0"),
    )
    op.create_index("ix_offers_lead_id", "offers", ["lead_id"])
    op.create_index("ix_offers_client_id", "offers", ["client_id"])

    op.create_table(
        "offer_items",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("offer_id", sa.String(), sa.ForeignKey("offers.id", ondelete="CASCADE"), nullable=False),
        sa.Column("product_id", sa.String(), sa.ForeignKey("products.id"), nullable=False),
        sa.Column("quantity", sa.Integer(), server_default="1"),
        sa.Column("unit_price", sa.Float(), server_default="0"),
        sa.Column("line_total", sa.Float(), server_default="0"),
        sa.Column("description", sa.Text()),
    )
    op.create_index("ix_offer_items_offer_id", "offer_items", ["offer_id"])


def downgrade():
    op.drop_index("ix_offer_items_offer_id", table_name="offer_items")
    op.drop_table("offer_items")

    op.drop_index("ix_offers_client_id", table_name="offers")
    op.drop_index("ix_offers_lead_id", table_name="offers")
    op.drop_table("offers")

    op.drop_index("ix_products_active", table_name="products")
    op.drop_index("ix_products_name", table_name="products")
    op.drop_table("products")

