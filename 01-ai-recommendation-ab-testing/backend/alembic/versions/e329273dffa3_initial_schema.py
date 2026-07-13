"""initial schema

Revision ID: e329273dffa3
Revises:
Create Date: 2026-07-13 22:57:45.918274
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "e329273dffa3"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("username", sa.String(255), unique=True, nullable=False),
        sa.Column("email", sa.String(255), unique=True, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "items",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("category", sa.String(100), nullable=False),
        sa.Column("price", sa.Float(), nullable=False),
        sa.Column("metadata_json", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "experiments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("status", sa.String(50), server_default=sa.text("'draft'"), nullable=False),
        sa.Column("traffic_split", sa.Float(), server_default=sa.text("0.5"), nullable=False),
        sa.Column("variant_a_label", sa.String(100), server_default=sa.text("'collaborative_filtering'"), nullable=False),
        sa.Column("variant_b_label", sa.String(100), server_default=sa.text("'deep_learning'"), nullable=False),
        sa.Column("start_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("end_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "interactions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("item_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("items.id"), nullable=False),
        sa.Column("interaction_type", sa.String(50), nullable=False),
        sa.Column("experiment_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("experiments.id"), nullable=True),
        sa.Column("variant", sa.String(50), nullable=True),
        sa.Column("revenue", sa.Float(), nullable=True),
        sa.Column("timestamp", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "assignments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("experiment_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("experiments.id"), nullable=False),
        sa.Column("variant", sa.String(50), nullable=False),
        sa.Column("assigned_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_index("ix_interactions_user_experiment", "interactions", ["user_id", "experiment_id"])
    op.create_index("ix_assignments_user_experiment", "assignments", ["user_id", "experiment_id"])
    op.create_index("ix_users_username", "users", ["username"])
    op.create_index("ix_items_category", "items", ["category"])


def downgrade() -> None:
    op.drop_table("assignments")
    op.drop_table("interactions")
    op.drop_table("experiments")
    op.drop_table("items")
    op.drop_table("users")
