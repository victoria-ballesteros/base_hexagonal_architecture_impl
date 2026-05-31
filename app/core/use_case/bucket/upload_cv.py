from app.ports.driving.storage_bucket_interfaz import StorageBucketInterfaceABC
from app.ports.driving.handler_interface import HandlerInterface
from app.domain.dtos.bucket_dto import UploadCVDTO
from app.domain.exceptions.base_exceptions import (
    InvalidFileTypeError,
    FileSizeExceededError,
    BucketNotFoundError,
)
from io import BytesIO


class UploadCVHandler(HandlerInterface):
    MAX_FILE_SIZE = 20 * 1024 * 1024

    def __init__(self, storage: StorageBucketInterfaceABC) -> None:
        self._storage = storage

    async def execute(self, dto: UploadCVDTO) -> dict:
        if dto.content_type != "application/pdf":
            raise InvalidFileTypeError(
                expected="application/pdf", received=dto.content_type, field="cv"
            )

        dto.file_data.seek(0)
        file_bytes = dto.file_data.read()
        if len(file_bytes) > self.MAX_FILE_SIZE:
            raise FileSizeExceededError(
                max_size_mb=self.MAX_FILE_SIZE / (1024 * 1024),
                actual_size_mb=len(file_bytes) / (1024 * 1024),
                field="cv",
            )

        path = f"cv_{dto.user_id}.pdf"

        try:
            url = await self._storage.upload_file(
                bucket="cvs",
                path=path,
                file_data=BytesIO(file_bytes),
                content_type="application/pdf",
            )
            return {"url": url, "path": path, "expires_in": 3600}
        except ValueError as e:
            if "Bucket" in str(e) and "no configurado" in str(e):
                raise BucketNotFoundError(bucket="cvs")
            raise
