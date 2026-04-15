"""Add ingredient-based stock tables.

Revision ID: 20260416_01
Revises:
Create Date: 2026-04-16
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "20260416_01"
down_revision = None
branch_labels = None
depends_on = None


def _has_table(table_name: str) -> bool:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    return inspector.has_table(table_name)


def upgrade() -> None:
    if not _has_table("ingredients"):
        op.create_table(
            "ingredients",
            sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
            sa.Column("name", sa.String(length=120), nullable=False),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column("price_per_unit", sa.Numeric(12, 3), nullable=False),
            sa.Column("category", sa.String(length=80), nullable=False),
            sa.Column("stock_level", sa.Numeric(12, 3), nullable=False, server_default=sa.text("0")),
            sa.Column("min_stock", sa.Numeric(12, 3), nullable=False, server_default=sa.text("5")),
            sa.Column("unit_type", sa.String(length=50), nullable=False),
            sa.Column(
                "tags",
                postgresql.ARRAY(sa.String()),
                nullable=False,
                server_default=sa.text("'{}'::text[]"),
            ),
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                nullable=False,
                server_default=sa.text("CURRENT_TIMESTAMP"),
            ),
            sa.Column(
                "updated_at",
                sa.DateTime(timezone=True),
                nullable=False,
                server_default=sa.text("CURRENT_TIMESTAMP"),
            ),
            sa.UniqueConstraint("name", name="uq_ingredients_name"),
        )
        op.create_index("ix_ingredients_name", "ingredients", ["name"], unique=False)
        op.create_index("ix_ingredients_category", "ingredients", ["category"], unique=False)

    if not _has_table("dishes"):
        op.create_table(
            "dishes",
            sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
            sa.Column("name", sa.String(length=120), nullable=False),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column("price", sa.Numeric(12, 2), nullable=False),
            sa.Column("category", sa.String(length=80), nullable=False),
            sa.Column(
                "tags",
                postgresql.ARRAY(sa.String()),
                nullable=False,
                server_default=sa.text("'{}'::text[]"),
            ),
            sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                nullable=False,
                server_default=sa.text("CURRENT_TIMESTAMP"),
            ),
            sa.Column(
                "updated_at",
                sa.DateTime(timezone=True),
                nullable=False,
                server_default=sa.text("CURRENT_TIMESTAMP"),
            ),
            sa.UniqueConstraint("name", name="uq_dishes_name"),
        )
        op.create_index("ix_dishes_name", "dishes", ["name"], unique=False)
        op.create_index("ix_dishes_category", "dishes", ["category"], unique=False)

    if not _has_table("dish_ingredients"):
        op.create_table(
            "dish_ingredients",
            sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
            sa.Column("dish_id", sa.Integer(), nullable=False),
            sa.Column("ingredient_id", sa.Integer(), nullable=False),
            sa.Column("quantity_needed", sa.Numeric(12, 3), nullable=False),
            sa.ForeignKeyConstraint(["dish_id"], ["dishes.id"], ondelete="CASCADE"),
            sa.ForeignKeyConstraint(["ingredient_id"], ["ingredients.id"], ondelete="CASCADE"),
            sa.UniqueConstraint("dish_id", "ingredient_id", name="uq_dish_ingredient"),
        )
        op.create_index("ix_dish_ingredients_dish_id", "dish_ingredients", ["dish_id"], unique=False)
        op.create_index(
            "ix_dish_ingredients_ingredient_id", "dish_ingredients", ["ingredient_id"], unique=False
        )

    if not _has_table("stock_transactions"):
        op.create_table(
            "stock_transactions",
            sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
            sa.Column("ingredient_id", sa.Integer(), nullable=False),
            sa.Column("transaction_type", sa.String(length=20), nullable=False),
            sa.Column("quantity_changed", sa.Numeric(12, 3), nullable=False),
            sa.Column("reference_type", sa.String(length=50), nullable=True),
            sa.Column("reference_id", sa.Integer(), nullable=True),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column("created_by", sa.String(length=100), nullable=True),
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                nullable=False,
                server_default=sa.text("CURRENT_TIMESTAMP"),
            ),
            sa.ForeignKeyConstraint(["ingredient_id"], ["ingredients.id"]),
        )
        op.create_index(
            "ix_stock_transactions_ingredient_id", "stock_transactions", ["ingredient_id"], unique=False
        )
        op.create_index(
            "ix_stock_transactions_created_at", "stock_transactions", ["created_at"], unique=False
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    existing_tables = set(inspector.get_table_names())
    if "stock_transactions" in existing_tables:
        op.drop_table("stock_transactions")
    if "dish_ingredients" in existing_tables:
        op.drop_table("dish_ingredients")
    if "dishes" in existing_tables:
        op.drop_table("dishes")
    if "ingredients" in existing_tables:
        op.drop_table("ingredients")
