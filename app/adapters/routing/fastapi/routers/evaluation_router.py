from typing import Any

from fastapi import APIRouter, Depends  # type: ignore

from app.adapters.database.dependencies import (
    RequireRoles,
    get_assign_project_evaluator_handler,
    get_update_team_score_feedback_handler,
    get_evaluators_handler,
    get_update_team_votes_handler,
)
from app.adapters.routing.utils.decorators import format_response
from app.adapters.routing.utils.response import ResultSchema
from app.domain.dtos.team_dto import (
    AssignProjectEvaluatorInputDTO,
    AssignProjectEvaluatorResponseDTO,
    UpdateTeamScoreFeedbackInputDTO,
    UpdateTeamScoreFeedbackResponseDTO,
)
from app.domain.exceptions.base_exceptions import UnauthorizedException
from app.ports.driving.handler_interface import HandlerInterface
from app.adapters.routing.utils.context import user_context

router = APIRouter(prefix="/evaluations", tags=["Evaluations"])


def _get_current_user_id() -> int:
    current_user = user_context.get()
    if not current_user or current_user.id is None:
        raise UnauthorizedException("Authentication required")
    return current_user.id


@router.post(
    "/{team_id}/project-evaluator",
    response_model=ResultSchema[AssignProjectEvaluatorResponseDTO],
)
@format_response
def assign_project_evaluator(
    team_id: int,
    data: AssignProjectEvaluatorInputDTO,
    _=Depends(RequireRoles(["admin"], [])),
    use_case: HandlerInterface = Depends(get_assign_project_evaluator_handler),
) -> Any:
    return use_case.execute(_get_current_user_id(), team_id, data)


@router.post(
    "/score-feedback/{team_id}",
    response_model=ResultSchema[UpdateTeamScoreFeedbackResponseDTO],
)
@format_response
def update_team_score_feedback(
    team_id: int,
    data: UpdateTeamScoreFeedbackInputDTO,
    _=Depends(RequireRoles(["evaluator"], [])),
    use_case: HandlerInterface = Depends(get_update_team_score_feedback_handler),
) -> Any:
    return use_case.execute(_get_current_user_id(), team_id, data)


@router.get(
    "/evaluators",
    response_model=ResultSchema[list],
)
@format_response
def list_evaluators(
    _=Depends(RequireRoles(["admin"], [])),
    handler: HandlerInterface = Depends(get_evaluators_handler),
) -> Any:
    return handler.execute()


@router.post(
    "/{team_id}/votes",
    response_model=ResultSchema[UpdateTeamScoreFeedbackResponseDTO],
)
@format_response
def update_team_votes(
    team_id: int,
    data: UpdateTeamScoreFeedbackInputDTO,
    _=Depends(RequireRoles(["admin"], [])),
    use_case: HandlerInterface = Depends(get_update_team_votes_handler),
) -> Any:
    # Reuse UpdateTeamScoreFeedbackInputDTO to accept votes_qty via `score` field.
    votes_qty = data.score
    feedback = data.feedback
    return use_case.execute(team_id, votes_qty, feedback)
