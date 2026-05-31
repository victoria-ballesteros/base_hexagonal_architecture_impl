from sqlalchemy.orm import Session
from app.adapters.database.postgres.models.role_model import Role

from app.domain.dtos.role_dto import RoleDTO
from app.ports.driven.database.postgres.role_repository import RoleRepositoryInterface


class RoleRepository(RoleRepositoryInterface):
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, role_id: int) -> RoleDTO | None:
        query_result = self.db.query(Role).filter_by(id=role_id).first()
        return RoleDTO.from_orm(query_result) if query_result else None

    def get_by_internal_code(self, code: str) -> RoleDTO | None:
        query_result = self.db.query(Role).filter_by(internal_code=code).first()
        return RoleDTO.from_orm(query_result) if query_result else None
        