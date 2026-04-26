"""Repair team review columns

Revision ID: 7c2a9b8e4f10
Revises: 6b1e7f57d3aa
Create Date: 2026-04-26 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision: str = "7c2a9b8e4f10"
down_revision: Union[str, None] = "6b1e7f57d3aa"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = inspect(conn)

    if "team" not in inspector.get_table_names():
        return

    existing_columns = {column["name"] for column in inspector.get_columns("team")}

    if "status" not in existing_columns:
        op.add_column(
            "team",
            sa.Column("status", sa.Integer(), nullable=False, server_default=sa.text("0")),
        )
        conn.execute(sa.text("UPDATE team SET status = 0 WHERE status IS NULL"))

    if "feedback" not in existing_columns:
        op.add_column("team", sa.Column("feedback", sa.String(), nullable=True))

    if "project_evaluator_id" not in existing_columns:
        op.add_column(
            "team",
            sa.Column(
                "project_evaluator_id",
                sa.Integer(),
                sa.ForeignKey("user.id", ondelete="SET NULL"),
                nullable=True,
            ),
        )


def downgrade() -> None:
    conn = op.get_bind()
    inspector = inspect(conn)

    if "team" not in inspector.get_table_names():
        return

    existing_columns = {column["name"] for column in inspector.get_columns("team")}

    if "project_evaluator_id" in existing_columns:
        op.drop_column("team", "project_evaluator_id")

    if "feedback" in existing_columns:
        op.drop_column("team", "feedback")

    if "status" in existing_columns:
        op.drop_column("team", "status")
