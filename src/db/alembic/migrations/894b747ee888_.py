"""empty message

Revision ID: 894b747ee888
Revises: 
Create Date: 2025-10-11 11:09:16.753125

"""
from typing import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "894b747ee888"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "orders",
        sa.Column("id", sa.UUID(), autoincrement=False, nullable=False),
        sa.Column("user_name", sa.String(length=256), nullable=False),
        sa.Column("phone_number", sa.String(length=32), nullable=False),
        sa.Column(
            "status",
            sa.Enum("CANCELED", "CONFIRMED", "PENDING", name="order_status_enum"),
            nullable=False,
        ),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("phone_number"),
    )
    op.create_table(
        "users",
        sa.Column("username", sa.String(length=64), nullable=False),
        sa.Column("password", sa.Text(), nullable=False),
        sa.Column("role", sa.Enum("ADMIN", "USER", name="user_role_enum"), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("created", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("username"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("users")
    op.drop_table("orders")
