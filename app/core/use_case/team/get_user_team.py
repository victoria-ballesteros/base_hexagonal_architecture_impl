from app.ports.driven.database.postgres.team_repository_abc import TeamRepositoryInterface
from app.ports.driving.handler_interface import HandlerInterface
from app.domain.dtos.team_dto import (
    ListTeamsDisplayResponseDTO,
    TeamListItemDisplayDTO,
    TeamDisplayDTO,
)
from app.ports.driving.storage_bucket_interfaz import StorageBucketInterfaceABC
from app.domain.exceptions.base_exceptions import (
    TeamNotFoundException,
)


class GetUserTeamHandler(HandlerInterface):
    def __init__(
        self, team_query: TeamRepositoryInterface, storage: StorageBucketInterfaceABC
    ):
        self._team_query = team_query
        self._storage = storage

    async def execute_async(self, user_id: str) -> ListTeamsDisplayResponseDTO:

        if not user_id or not isinstance(user_id, str):
            raise TeamNotFoundException(user_id="invalid")

        user_team = self._team_query.get_user_team(user_id)
        if user_team and user_team.team_id:
            # user_team.team is TeamResponseDTO instance
            team_resp = user_team
            # create TeamDisplayDTO
            evaluation_id = getattr(team_resp, "evaluation_id", None)
            evaluation_url = None
            if evaluation_id is not None:
                file_name = self._team_query.get_evaluation_file_name(evaluation_id)
                if file_name:
                    evaluation_url = await self._storage.get_signed_url(
                        bucket="exercises", path=file_name, expires_in=3600
                    )

            team_display = TeamDisplayDTO(
                id=int(team_resp.team_id),
                name=team_resp.team_name,
                logo=None,
                score=getattr(team_resp, "status", None),
                standing_position=None,
                cloud_repo_link=None,
                status=getattr(team_resp, "status", 0),
                feedback=getattr(team_resp, "feedback", None),
                edition_id=int(team_resp.edition_id),
                category_name="",
                evaluation_id=evaluation_id,
                evaluation_file_url=evaluation_url,
                assigned_evaluator_username=None,
                project_evaluator_username=None,
            )

            item = TeamListItemDisplayDTO(team=team_display, leader=None, members_count=0)
            return ListTeamsDisplayResponseDTO(teams=[item])

        raise TeamNotFoundException(user_id=user_id)

    def execute(self, *args, **kwargs):
        return self.execute_async(*args, **kwargs)
