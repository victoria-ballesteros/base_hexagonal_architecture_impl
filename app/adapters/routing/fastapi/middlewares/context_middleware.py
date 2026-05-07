from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint # type: ignore
from starlette.requests import Request # type: ignore
from starlette.responses import Response # type: ignore
from app.adapters.routing.utils.context import user_context


class UserContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        token = user_context.set(None)
        try:
            response = await call_next(request)
            return response
        finally:
            user_context.reset(token)
