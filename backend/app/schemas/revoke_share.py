from pydantic import BaseModel


class RevokeShareRequest(BaseModel):
    share_id: int


class RevokeShareResponse(BaseModel):
    message: str
    is_active: bool