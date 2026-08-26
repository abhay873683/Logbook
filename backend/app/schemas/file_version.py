from datetime import datetime

from pydantic import BaseModel, ConfigDict


class FileVersionCreate(BaseModel):
    file_id: int


class FileVersionResponse(BaseModel):
    id: int
    file_id: int
    version_number: int
    file_path: str
    file_size: int | None = None
    uploaded_by: int
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )