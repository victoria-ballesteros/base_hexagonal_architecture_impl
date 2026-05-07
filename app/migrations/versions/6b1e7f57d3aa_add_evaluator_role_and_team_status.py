"""Add evaluator role and team status

Revision ID: 6b1e7f57d3aa
Revises: 4b7f2e1a8d9c
Create Date: 2026-04-21 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision: str = "6b1e7f57d3aa"
down_revision: Union[str, None] = "4b7f2e1a8d9c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = inspect(conn)
    existing_tables = set(inspector.get_table_names())

    if "team" in existing_tables:
        existing_columns = {column["name"] for column in inspector.get_columns("team")}

        if "status" not in existing_columns:
            op.add_column(
                "team",
                sa.Column(
                    "status",
                    sa.Integer(),
                    nullable=False,
                    server_default=sa.text("0"),
                ),
            )

            conn.execute(sa.text("UPDATE team SET status = 0 WHERE status IS NULL"))

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

        if "feedback" not in existing_columns:
            op.add_column(
                "team",
                sa.Column("feedback", sa.String(), nullable=True),
            )

    if "role" in existing_tables:
        evaluator_role_exists = conn.execute(
            sa.text(
                """
                SELECT 1
                FROM role
                WHERE internal_code = :internal_code
                """
            ),
            {"internal_code": "evaluator"},
        ).fetchone()

        if not evaluator_role_exists:
            conn.execute(
                sa.text(
                    """
                    INSERT INTO role (name, description, is_super_user, internal_code)
                    VALUES (:name, :description, :is_super_user, :internal_code)
                    """
                ),
                {
                    "name": "Evaluator",
                    "description": "User with evaluator privileges",
                    "is_super_user": False,
                    "internal_code": "evaluator",
                },
            )

        # Evaluator seeding
        role_evaluator_id = conn.execute(
            sa.text("SELECT id FROM role WHERE internal_code = 'evaluator'")
        ).fetchone()[0]

        cat_id_row = conn.execute(
            sa.text("SELECT id FROM category WHERE internal_code = 'cat_general'")
        ).fetchone()

        if not cat_id_row:
            cat_id_row = conn.execute(sa.text("SELECT id FROM category LIMIT 1")).fetchone()

        cat_id = cat_id_row[0] if cat_id_row else None

        default_hash = "$argon2id$v=19$m=65536,t=3,p=4$+t9b693b2xsjpNR6j7GWMg$3IB15WbxlyCIpV7kT1IXTP/4DIqj2De0m6MQa3zze7E"
        evaluator_email = "evaluador@unet.edu.ve"

        evaluator_user_exists = conn.execute(
            sa.text("SELECT 1 FROM \"user\" WHERE email =:email"),
            {"email": evaluator_email}
        ).fetchone()

        if not evaluator_user_exists:
            conn.execute(
                sa.text(
                    """
                    INSERT INTO "user" (username, name, email, password_hash, status, role_id, category_id, is_verified)
                    VALUES (:username, :name, :email, :password_hash, :status, :role_id, :category_id, :is_verified)
                    """
                ),
                {
                    "username": "evaluador",
                    "name": "Profesor Evaluador",
                    "email": evaluator_email,
                    "password_hash": default_hash,
                    "status": "ACTIVE",
                    "role_id": role_evaluator_id,
                    "category_id": cat_id,
                    "is_verified": True
                }
            )


def downgrade() -> None:
    conn = op.get_bind()
    inspector = inspect(conn)
    existing_tables = set(inspector.get_table_names())

    if "role" in existing_tables:
        conn.execute(
            sa.text(
                """
                DELETE FROM role
                WHERE internal_code = :internal_code
                """
            ),
            {"internal_code": "evaluator"},
        )

    if "team" in existing_tables:
        existing_columns = {column["name"] for column in inspector.get_columns("team")}

        if "feedback" in existing_columns:
            op.drop_column("team", "feedback")

        if "project_evaluator_id" in existing_columns:
            op.drop_column("team", "project_evaluator_id")

        if "status" in existing_columns:
            op.drop_column("team", "status")
