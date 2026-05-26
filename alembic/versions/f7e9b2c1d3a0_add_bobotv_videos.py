"""add_bobotv_videos

Revision ID: f7e9b2c1d3a0
Revises: e643d43f001f
Create Date: 2026-05-25 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "f7e9b2c1d3a0"
down_revision: Union[str, Sequence[str], None] = "e643d43f001f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "bobotv_videos",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.String(length=256), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("s3_key", sa.String(length=1024), nullable=False),
        sa.Column("file_size", sa.Integer(), nullable=False),
        sa.Column("mime_type", sa.String(length=128), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("uploaded_by", sa.String(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "idx_bobotv_title",
        "bobotv_videos",
        ["title"],
    )
    op.create_index(
        "idx_bobotv_active_created",
        "bobotv_videos",
        ["is_active", "created_at"],
    )


def downgrade() -> None:
    op.drop_index("idx_bobotv_active_created", table_name="bobotv_videos")
    op.drop_index("idx_bobotv_title", table_name="bobotv_videos")
    op.drop_table("bobotv_videos")
