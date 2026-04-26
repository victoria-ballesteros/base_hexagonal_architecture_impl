from app.domain.dtos.team_dto import (
    UploadTeamRepositoryLinkInputDTO,
    UploadTeamRepositoryLinkResponseDTO,
)
from app.domain.exceptions.base_exceptions import DomainException
from app.domain.exceptions.error_codes import TEAM_LEADER_TEAM_NOT_FOUND
from app.ports.driven.database.postgres.team_repository_abc import (
    TeamRepositoryInterface,
)
from app.ports.driving.handler_interface import HandlerInterface


class UploadTeamRepositoryLinkHandler(HandlerInterface):
    def __init__(self, team_repository: TeamRepositoryInterface) -> None:
        self._team_repository = team_repository

    def execute(
        self,
        current_user_id: int,
        data: UploadTeamRepositoryLinkInputDTO,
    ) -> UploadTeamRepositoryLinkResponseDTO:
        team = self._team_repository.get_team_by_leader_id(current_user_id)
        if team is None:
            raise DomainException(
                "The authenticated user has not created a team",
                TEAM_LEADER_TEAM_NOT_FOUND,
            )

        updated_team = self._team_repository.update_team_repository_link(
            team.id,
            data.repository_link,
        )

        return UploadTeamRepositoryLinkResponseDTO(team=updated_team)
