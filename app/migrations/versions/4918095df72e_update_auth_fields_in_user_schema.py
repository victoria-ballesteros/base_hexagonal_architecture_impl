"""Update auth fields in user schema

Revision ID: 4918095df72e
Revises: 88020d66694c
Create Date: 2026-03-22 19:09:52.711722

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision: str = '4918095df72e'
down_revision: Union[str, None] = '88020d66694c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    inst = inspect(conn)
    existing_columns = [c["name"] for c in inst.get_columns("user")]

    if "is_verified" not in existing_columns:
        op.add_column(
            "user",
            sa.Column(
                "is_verified",
                sa.Boolean(),
                server_default=sa.text("false"),
                nullable=False,
            ),
        )

    if "verification_token" not in existing_columns:
        op.add_column(
            "user", sa.Column("verification_token", sa.String(), nullable=True)
        )

    if "verification_expires_at" not in existing_columns:
        op.add_column(
            "user",
            sa.Column(
                "verification_expires_at", sa.DateTime(timezone=True), nullable=True
            ),
        )


def downgrade() -> None:
    conn = op.get_bind()
    inst = inspect(conn)
    existing_columns = [c["name"] for c in inst.get_columns("user")]

    if "verification_expires_at" in existing_columns:
        op.drop_column("user", "verification_expires_at")

    if "verification_token" in existing_columns:
        op.drop_column("user", "verification_token")

    if "is_verified" in existing_columns:
        op.drop_column("user", "is_verified")