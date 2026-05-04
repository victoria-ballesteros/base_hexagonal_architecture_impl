from typing import List

from app.ports.driving.team_interface import TeamQueryInterface
from app.ports.driving.handler_interface import HandlerInterface
from app.domain.dtos.team_dto import UserListDTO


class GetEvaluatorsHandler(HandlerInterface):
    def __init__(self, team_query: TeamQueryInterface):
        self._team_query = team_query

    def execute(self) -> List[UserListDTO]:
        return self._team_query.get_users_by_role("evaluator")
