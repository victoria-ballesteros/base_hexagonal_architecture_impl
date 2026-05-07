from contextvars import ContextVar
from typing import Optional

from sqlalchemy.orm import Session

from app.domain.dtos.user_dto import UserDTO

db_context: ContextVar[Optional[Session]] = ContextVar("db_context", default=None)

user_context: ContextVar[Optional[UserDTO]] = ContextVar("user_context", default=None)
