from app.domain.dtos.team_dto import (
    UpdateTeamScoreFeedbackInputDTO,
    UpdateTeamScoreFeedbackResponseDTO,
)
from app.domain.exceptions.base_exceptions import DomainException
from app.domain.exceptions.error_codes import TEAM_NOT_FOUND, TEAM_CATEGORY_NOT_ALLOWED
from app.ports.driven.database.postgres.team_repository_abc import (
    TeamRepositoryInterface,
)
from app.ports.driving.handler_interface import HandlerInterface


class UpdateTeamScoreFeedbackHandler(HandlerInterface):
    def __init__(self, team_repository: TeamRepositoryInterface) -> None:
        self._team_repository = team_repository

    def execute(self, current_user_id: int, team_id: int, data: UpdateTeamScoreFeedbackInputDTO) -> UpdateTeamScoreFeedbackResponseDTO:
        team = self._team_repository.get_team_by_id(team_id)
        if team is None:
            raise DomainException("Team not found", TEAM_NOT_FOUND)

        # ensure team category is 'junior'
        is_junior = self._team_repository.is_team_category(team_id, "junior")
        if not is_junior:
            raise DomainException("Team must belong to junior category", TEAM_CATEGORY_NOT_ALLOWED)
        
        if data.score is not None and (data.score < 0 or data.score > 100):
            raise DomainException("Score must be between 0 and 100")

        # update fields (score and/or feedback). Both optional.
        updated_team = self._team_repository.update_team_score_feedback(team_id, data.score, data.feedback)

        return UpdateTeamScoreFeedbackResponseDTO(team=updated_team)
