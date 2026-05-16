"""Add description field to team model

Revision ID: 7817795b4b2c
Revises: a8f7c3d2e9b1
Create Date: 2026-05-16 23:24:42.904409

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7817795b4b2c'
down_revision: Union[str, None] = 'a8f7c3d2e9b1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    cols = [c["name"] for c in inspector.get_columns("team")]
    if "description" not in cols:
        op.add_column("team", sa.Column("description", sa.String, nullable=True))
        op.execute(
            "UPDATE team SET description = 'Sin descripción' WHERE description IS NULL"
        )
        op.alter_column("team", "description", nullable=False)


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    cols = [c["name"] for c in inspector.get_columns("team")]
    if "description" in cols:
        op.drop_column("team", "description")
