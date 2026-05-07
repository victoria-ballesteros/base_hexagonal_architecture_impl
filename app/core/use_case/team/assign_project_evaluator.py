from app.domain.dtos.team_dto import (
    AssignProjectEvaluatorInputDTO,
    AssignProjectEvaluatorResponseDTO,
)
from app.domain.exceptions.base_exceptions import DomainException, RecordNotFoundException
from app.domain.exceptions.error_codes import TEAM_NOT_FOUND, TEAM_USER_NOT_EVALUATOR
from app.ports.driven.database.postgres.team_repository_abc import (
    TeamRepositoryInterface,
)
from app.ports.driving.handler_interface import HandlerInterface


class AssignProjectEvaluatorHandler(HandlerInterface):
    def __init__(self, team_repository: TeamRepositoryInterface) -> None:
        self._team_repository = team_repository

    def execute(self, current_user_id: int, team_id: int, data: AssignProjectEvaluatorInputDTO) -> AssignProjectEvaluatorResponseDTO:
        team = self._team_repository.get_team_by_id(team_id)
        if team is None:
            raise DomainException("Team not found", TEAM_NOT_FOUND)

        user = self._team_repository.get_user_by_id(data.user_id)
        if user is None:
            raise RecordNotFoundException("USER")

        # Ensure the provided user has the evaluator role
        is_evaluator = self._team_repository.is_user_role(data.user_id, "evaluator")
        if not is_evaluator:
            raise DomainException("The specified user is not an evaluator", TEAM_USER_NOT_EVALUATOR)

        updated_team = self._team_repository.update_project_evaluator(team_id, data.user_id)

        return AssignProjectEvaluatorResponseDTO(team=updated_team)
