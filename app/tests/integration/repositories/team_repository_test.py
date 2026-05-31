from app.adapters.database.postgres.connection import SessionLocal
from app.adapters.database.postgres.models.team_model import Team
from app.adapters.database.postgres.models.user_model import User
from app.adapters.database.postgres.models.user_model import (
    team_request_association,
    user_team_association,
)
from app.domain.dtos.team_dto import (
    GetUserTeamResponseDTO,
    UploadTeamRepositoryLinkInputDTO,
)
from app.domain.enums import TeamRequestStatus
from app.domain.exceptions.base_exceptions import TeamNotFoundException
from app.ports.driving.team_interface import TeamQueryInterface
from pydantic import ValidationError
import pytest # type: ignore
from app.adapters.database.postgres.repositories.team_repository import TeamRepository


@pytest.fixture
def db_session():
    return SessionLocal()

@pytest.fixture
def repo(db_session) -> TeamQueryInterface:
    return TeamRepository(db_session)

def test_get_active_users_from_migration(repo: TeamQueryInterface) -> None:
    active_users = repo.get_active_users()
    emails = [u.email for u in active_users]

    assert "daniel.bautista.test@unet.edu.ve" in emails
    assert "douglas.moreno.test@unet.edu.ve" in emails
    assert "maria.ballesteros@unet.edu.ve" not in emails


def test_list_teams_table_returns_frontend_columns(db_session) -> None:
    team = db_session.query(Team).filter_by(name="UNET Cyber-Warriors").first()
    leader = db_session.query(User).filter_by(email="daniel.bautista.test@unet.edu.ve").first()

    assert team is not None, "The migration did not load the expected team"
    assert leader is not None, "The migration did not load the user Daniel"

    original_status = team.status
    original_cloud_repo_link = team.cloud_repo_link
    original_score = team.score
    original_feedback = team.feedback
    original_assigned_evaluator_id = team.assigned_evaluator_id

    try:
        team.status = 2
        team.cloud_repo_link = "https://github.com/example/project"
        team.score = 95
        team.feedback = "Ready for table view"
        team.assigned_evaluator_id = leader.id
        db_session.commit()

        response = TeamRepository(db_session).list_teams_table()
        row = next(item for item in response if item.team_name == "UNET Cyber-Warriors")

        assert row.team_name == "UNET Cyber-Warriors"
        assert row.leader_name == leader.name
        assert row.evaluator is None
        assert row.repository_link == "https://github.com/example/project"
        assert row.status == "En revision"
        assert row.score == 95
        assert row.feedback == "Ready for table view"
        assert row.updated_at is not None
    finally:
        team.status = original_status
        team.cloud_repo_link = original_cloud_repo_link
        team.score = original_score
        team.feedback = original_feedback
        team.assigned_evaluator_id = original_assigned_evaluator_id
        db_session.commit()


def test_upload_team_repository_link_input_rejects_non_github_url() -> None:
    with pytest.raises(ValidationError):
        UploadTeamRepositoryLinkInputDTO(
            repository_link="https://gitlab.com/example/project"
        )


def test_update_team_repository_link_sets_status_pending(db_session) -> None:
    team = db_session.query(Team).filter_by(name="UNET Cyber-Warriors").first()

    assert team is not None, "The migration did not load the expected team"

    original_status = team.status
    original_cloud_repo_link = team.cloud_repo_link

    try:
        updated_team = TeamRepository(db_session).update_team_repository_link(
            team.id,
            "https://github.com/example/project",
        )

        assert updated_team.cloud_repo_link == "https://github.com/example/project"
        assert updated_team.status == 1
    finally:
        team.status = original_status
        team.cloud_repo_link = original_cloud_repo_link
        db_session.commit()


def test_get_user_team_not_found_real_user(repo, db_session) -> None:
    user = db_session.query(User).filter_by(email="maria.ballesteros@unet.edu.ve").first()

    assert user is not None, "The migration did not load the user Maria"

    with pytest.raises(TeamNotFoundException):
        repo.get_user_team(str(user.id))


def test_get_user_team_info_is_correct(repo, db_session):
    user = db_session.query(User).filter_by(email="daniel.bautista.test@unet.edu.ve").first()
    assert user is not None, "The migration did not load the user Daniel"
    team = db_session.query(Team).filter_by(name="UNET Cyber-Warriors").first()
    assert team is not None, "The migration did not load the expected team"

    response = repo.get_user_team(str(user.id))

    assert isinstance(response, GetUserTeamResponseDTO)
    assert response.team_name == "UNET Cyber-Warriors"
    assert response.edition_name == "First Edition 2026"
    assert response.status == team.status
    assert response.feedback == team.feedback
    assert response.assigned_evaluator_id == team.assigned_evaluator_id
    assert response.project_evaluator_id == team.project_evaluator_id

    assert len(response.accepted_members) > 0
    member = response.accepted_members[0]
    assert member.email == "daniel.bautista.test@unet.edu.ve"
    assert member.username == "dbautista"
    assert member.status == TeamRequestStatus.ACCEPTED.name

    assert len(response.pending_members) == 0
    assert len(response.deleted_members) == 0


def test_get_user_team_uses_receiver_for_invited_members(repo, db_session):
    leader = db_session.query(User).filter_by(email="daniel.bautista.test@unet.edu.ve").first()
    invitee = db_session.query(User).filter_by(email="maria.ballesteros@unet.edu.ve").first()
    team = db_session.query(Team).filter_by(name="UNET Cyber-Warriors").first()

    assert leader is not None
    assert invitee is not None
    assert team is not None

    inserted_request_id = None
    inserted_user_team = False

    try:
        user_team_exists = db_session.execute(
            user_team_association.select().where(
                user_team_association.c.user_id == invitee.id,
                user_team_association.c.team_id == team.id,
            )
        ).first()

        if user_team_exists is None:
            db_session.execute(
                user_team_association.insert().values(
                    user_id=invitee.id,
                    team_id=team.id,
                )
            )
            inserted_user_team = True

        inserted_request = db_session.execute(
            team_request_association.insert()
            .values(
                team_id=team.id,
                sender_user_id=leader.id,
                receiver_user_id=invitee.id,
                status=TeamRequestStatus.ACCEPTED,
            )
            .returning(team_request_association.c.id)
        ).first()

        assert inserted_request is not None
        inserted_request_id = inserted_request.id
        db_session.commit()

        response = repo.get_user_team(str(leader.id))
        accepted_emails = [member.email for member in response.accepted_members]

        assert leader.email in accepted_emails
        assert invitee.email in accepted_emails
        assert accepted_emails.count(leader.email) == 1
    finally:
        if inserted_request_id is not None:
            db_session.execute(
                team_request_association.delete().where(
                    team_request_association.c.id == inserted_request_id
                )
            )
            if inserted_user_team:
                db_session.execute(
                    user_team_association.delete().where(
                        user_team_association.c.user_id == invitee.id,
                        user_team_association.c.team_id == team.id,
                    )
                )
            db_session.commit()
