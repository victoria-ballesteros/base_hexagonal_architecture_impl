import logging
from sqlalchemy.orm import Session

from app.adapters.database.postgres.models.category_model import Category
from app.adapters.database.postgres.models.edition_model import Edition
from datetime import datetime, timezone, timedelta

from app.adapters.database.postgres.models.evaluation_model import Evaluation
from app.adapters.database.postgres.models.role_model import Role
from app.adapters.database.postgres.models.sponsor_model import SocialMediaDefinition, Sponsor
from app.adapters.database.postgres.models.team_model import Team
from app.adapters.database.postgres.models.user_model import User, user_team_association, team_request_association
from app.ports.driving.seeder_interface import SeederInterface
from app.domain.enums import CompanyType, SocialMedia, TeamRequestStatus


class DevelopmentDataSeeder(SeederInterface):
    def __init__(self, db: Session) -> None:
        self.db=db
        self.logger=logging.getLogger(__name__)

    def run(self, clear_existing: bool=True) -> None:
        try:
            if clear_existing:
                self._clear_tables()

                self.logger.info("Development data seeding process started.")

                self._seed_tables()

                self.logger.info("Development data seeding process finished.")
            
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Error in development data model seeder: {str(e)}")
            raise

    def _clear_tables(self) -> None:
        self._clear_associations()

        self._clear_general_table("Edition", Edition)
        self._clear_general_table("Sponsor", Sponsor)
        self._clear_general_table("Role", Role)
        self._clear_general_table("Category", Category)
        self._clear_general_table("User", User)
        self._clear_general_table("Evaluation", Evaluation)
        self._clear_general_table("Team", Team)

    def _seed_tables(self) -> None:
        edition = self._seed_edition_table()
        self._seed_sponsor_table(edition.id)

        roles = self._seed_role_table()
        category = self._seed_category_table()

        users = self._seed_user_table(roles, category)
        self._seed_evaluation_table(category.id)

        team = self._seed_team_model(
            edition.id, category.id, users[0].id
        )

        self._seed_associations(users, team)

    def _seed_edition_table(self) -> Edition:
        edition = Edition(
            name="HWC: SECOND EDITION",
            start_date=datetime.now(timezone.utc),
            end_date=datetime.now(timezone.utc) + timedelta(days=2),
        )
        self.db.add(edition)
        self.db.commit()
        self.db.refresh(edition)
        return edition

    def _seed_sponsor_table(self, edition_id: int) -> None:
        social_data = SocialMediaDefinition(
            type=SocialMedia.TEST_SOCIAL_MEDIA.value, identity="@usuario"
        )
        sponsor = Sponsor(
            company_name="Nombre",
            company_type=CompanyType.TEST_COMPANY.value,
            description="Descripción",
            slogan="Slogan",
            logo="nombre_del_logo.png",
            social_media=social_data,
            edition_id=edition_id,
        )
        self.db.add(sponsor)
        self.db.commit()

    def _seed_role_table(self) -> dict[str, Role]:
        roles = [
            Role(
                name="Super Admin",
                description="Privilegios totales",
                is_super_user=True,
                internal_code="super_admin",
            ),
            Role(
                name="Competidor",
                description="Privilegios de competidor",
                internal_code="competitor",
            ),
        ]
        for r in roles:
            self.db.add(r)
        self.db.commit()
        return {r.internal_code: r for r in roles}

    def _seed_category_table(self) -> Category:
        category = Category(
            name="Junior",
            open_date=datetime.now(timezone.utc),
            close_date=datetime.now(timezone.utc) + timedelta(days=2),
            internal_code="junior_test",
        )
        self.db.add(category)
        self.db.commit()
        self.db.refresh(category)
        return category

    def _seed_user_table(
        self, roles: dict[str, Role], category: Category
    ) -> list[User]:
        users = [
            User(
                username="super_admin",
                name="Super Admin",
                email="superadmin123@test.com",
                password_hash="password_hash",
                status=1,
                role_id=roles["super_admin"].id,
                category_id=None,
            ),
            User(
                username="test_user",
                name="Test User",
                email="testuser123@test.com",
                password_hash="password_hash",
                status=1,
                role_id=roles["competitor"].id,
                category_id=category.id,
            ),
        ]
        for u in users:
            self.db.add(u)
        self.db.commit()
        for u in users:
            self.db.refresh(u)
        return users

    def _seed_evaluation_table(self, category_id: int) -> Evaluation:
        evaluation = Evaluation(
            file_name="evaluation_filename.pdf", category_id=category_id
        )
        self.db.add(evaluation)
        self.db.commit()
        self.db.refresh(evaluation)
        return evaluation

    def _seed_team_model(
        self, edition_id: int, category_id: int, evaluator_id: int
    ) -> Team:
        team = Team(
            name="Team Test",
            logo="nombre_del_logo.png",
            edition_id=edition_id,
            category_id=category_id,
            assigned_evaluator_id=evaluator_id,
        )
        self.db.add(team)
        self.db.commit()
        self.db.refresh(team)
        return team

    def _seed_associations(self, users: list[User], team: Team) -> None:
        self.db.execute(
            user_team_association.insert().values( # type: ignore
                [{"user_id": users[1].id, "team_id": team.id}]
            )
        )

        self.db.execute(
            team_request_association.insert().values( # type: ignore
                [
                    {
                        "team_id": team.id,
                        "sender_user_id": users[0].id,
                        "receiver_user_id": users[1].id,
                        "status": TeamRequestStatus.PENDING.value,
                    },
                ]
            )
        )
        self.db.commit()

    def _clear_associations(self) -> None:
        self.db.execute(user_team_association.delete()) # type: ignore
        self.db.execute(team_request_association.delete())  # type: ignore
        self.db.commit()
        self.logger.info("Associations cleared.")

    def _seed_general_data(self, table_name: str, data: list) -> None:
        created_count=0

        for register in data:
            self.db.add(register)
            created_count += 1

        self.db.commit()
        self.logger.info(f"{table_name} table: {created_count} records created.")

    def _clear_general_table(self, model_name: str, model) -> None:
        deleted_count=self.db.query(model).delete()
        self.db.commit()
        self.logger.info(f"Deleted {deleted_count} existing records from {model_name}.")
        pass