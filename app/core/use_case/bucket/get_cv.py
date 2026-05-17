from app.ports.driving.storage_bucket_interfaz import StorageBucketInterfaceABC
from app.ports.driving.handler_interface import HandlerInterface
from app.domain.dtos.bucket_dto import GetCVDTO


class GetCVHandler(HandlerInterface):
    def __init__(self, storage: StorageBucketInterfaceABC) -> None:
        self._storage = storage

    async def execute(self, dto: GetCVDTO) -> dict:
        path = f"cv_{dto.user_id}.pdf"
        url = await self._storage.get_signed_url(
            bucket="cvs", path=path, expires_in=3600
        )
        return {
            "url": url,
            "expires_in": 3600,
            "message": "User CV URL retrieved successfully",
        }
