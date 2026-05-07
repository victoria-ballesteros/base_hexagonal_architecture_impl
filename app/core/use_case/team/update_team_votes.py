from app.ports.driven.database.postgres.team_repository_abc import TeamRepositoryInterface
from app.domain.exceptions.base_exceptions import RecordNotFoundException, ForbiddenException


class UpdateTeamVotesHandler:
    def __init__(self, team_repo: TeamRepositoryInterface) -> None:
        self.team_repo = team_repo

    def execute(self, team_id: int, votes_qty: int, feedback: str | None = None):
        if votes_qty is None or votes_qty < 0:
            raise ForbiddenException("Invalid votes quantity")

        return self.team_repo.update_team_votes_and_feedback(
            team_id, votes_qty, feedback
        )
