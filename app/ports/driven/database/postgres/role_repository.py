from abc import ABC, abstractmethod

from app.domain.dtos.role_dto import RoleDTO


class RoleRepositoryInterface(ABC):
    @abstractmethod
    def get_by_id(self, role_id: int) -> RoleDTO | None:
        pass

    @abstractmethod
    def get_by_internal_code(self, code: str) -> RoleDTO | None:
        pass
