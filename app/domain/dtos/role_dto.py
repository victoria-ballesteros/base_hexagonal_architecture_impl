from pydantic import BaseModel, ConfigDict # type: ignore


class RoleDTO(BaseModel):
    id: int
    name: str
    description: str
    is_super_user: bool
    internal_code: str

    model_config = ConfigDict(from_attributes=True)
