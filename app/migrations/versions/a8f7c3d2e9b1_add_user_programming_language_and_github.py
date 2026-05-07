"""Add user programming language and github profile

Revision ID: a8f7c3d2e9b1
Revises: 473d3303081e, 7c2a9b8e4f10
Create Date: 2026-05-07 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision: str = "a8f7c3d2e9b1"
down_revision: Union[str, tuple[str, str], None] = (
    "473d3303081e",
    "7c2a9b8e4f10",
)
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


programming_language_enum = sa.Enum(
    "JAVASCRIPT",
    "TYPESCRIPT",
    "PYTHON",
    "JAVA",
    "C_SHARP",
    "PHP",
    "GO",
    "RUBY",
    "RUST",
    "ELIXIR",
    "C_PLUS_PLUS",
    "KOTLIN",
    "SCALA",
    "SWIFT",
    "CLOJURE",
    "ERLANG",
    "HASKELL",
    "DART",
    "PERL",
    "R",
    "JULIA",
    name="programminglanguage",
)


def upgrade() -> None:
    conn = op.get_bind()
    inspector = inspect(conn)

    if "user" not in inspector.get_table_names():
        return

    programming_language_enum.create(conn, checkfirst=True)
    existing_columns = {column["name"] for column in inspector.get_columns("user")}

    if "programming_language" not in existing_columns:
        op.add_column(
            "user",
            sa.Column("programming_language", programming_language_enum, nullable=True),
        )

    if "github_profile" not in existing_columns:
        op.add_column("user", sa.Column("github_profile", sa.String(), nullable=True))


def downgrade() -> None:
    conn = op.get_bind()
    inspector = inspect(conn)

    if "user" in inspector.get_table_names():
        existing_columns = {column["name"] for column in inspector.get_columns("user")}

        if "github_profile" in existing_columns:
            op.drop_column("user", "github_profile")

        if "programming_language" in existing_columns:
            op.drop_column("user", "programming_language")

    programming_language_enum.drop(conn, checkfirst=True)
