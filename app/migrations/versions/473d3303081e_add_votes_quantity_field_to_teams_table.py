"""add_votes_quantity_field_to_teams_table

Revision ID: 473d3303081e
Revises: 6b1e7f57d3aa
Create Date: 2026-05-03 23:52:05.436314

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '473d3303081e'
down_revision: Union[str, None] = '6b1e7f57d3aa'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    cols = [c["name"] for c in inspector.get_columns("team")]
    if "votes_qty" not in cols:
        op.add_column("team", sa.Column("votes_qty", sa.Integer(), nullable=True))


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    cols = [c["name"] for c in inspector.get_columns("team")]
    if "votes_qty" in cols:
        op.drop_column("team", "votes_qty")
