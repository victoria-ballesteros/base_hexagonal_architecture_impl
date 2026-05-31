from app.domain.dtos.team_dto import ListTeamsTableResponseDTO
from app.ports.driven.database.postgres.team_repository_abc import (
    TeamRepositoryInterface,
)
from app.ports.driving.handler_interface import HandlerInterface


class ListTeamsTableHandler(HandlerInterface):
    def __init__(self, team_repository: TeamRepositoryInterface) -> None:
        self._team_repository = team_repository

    def execute(self) -> ListTeamsTableResponseDTO:
        teams = self._team_repository.list_teams_table()
        return ListTeamsTableResponseDTO(teams=teams)
