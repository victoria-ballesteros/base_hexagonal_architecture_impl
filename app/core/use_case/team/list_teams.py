from app.domain.dtos.team_dto import (
    ListTeamsResponseDTO,
    ListTeamsDisplayResponseDTO,
    TeamListItemDisplayDTO,
    TeamDisplayDTO,
)
from app.domain.dtos.user_dto import UserResponseDTO
from app.ports.driven.database.postgres.team_repository_abc import (
    TeamRepositoryInterface,
)
from app.ports.driving.handler_interface import HandlerInterface


class ListTeamsHandler(HandlerInterface):
    def __init__(self, team_repository: TeamRepositoryInterface) -> None:
        self._team_repository = team_repository

    def execute(self) -> ListTeamsDisplayResponseDTO:
        # use enriched listing to include category name and evaluator usernames
        rows = self._team_repository.list_teams_enriched()
        display_items = []
        for team_orm, leader_orm, members_count, category_name, project_evaluator_username in rows:
            team_display = TeamDisplayDTO(
                id=getattr(team_orm, "id"),
                name=getattr(team_orm, "name"),
                logo=getattr(team_orm, "logo", None),
                score=getattr(team_orm, "score", None),
                standing_position=getattr(team_orm, "standing_position", None),
                cloud_repo_link=getattr(team_orm, "cloud_repo_link", None),
                status=getattr(team_orm, "status", 0),
                feedback=getattr(team_orm, "feedback", None),
                edition_id=getattr(team_orm, "edition_id"),
                category_name=category_name,
                evaluation_id=getattr(team_orm, "evaluation_id", None),
                assigned_evaluator_username=(leader_orm.username if leader_orm else None),
                project_evaluator_username=project_evaluator_username,
            )

            display_items.append(
                TeamListItemDisplayDTO(
                    team=team_display,
                    leader=(UserResponseDTO.from_orm(leader_orm) if leader_orm else None),
                    members_count=members_count,
                )
            )

        return ListTeamsDisplayResponseDTO(teams=display_items)
