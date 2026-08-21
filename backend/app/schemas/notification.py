from pydantic import BaseModel
from datetime import datetime


# -----------------------------
# Create Notification
# -----------------------------
class NotificationCreate(BaseModel):
    user_id: int
    title: str
    message: str
    type: str = "info"


# -----------------------------
# Response
# -----------------------------
class NotificationResponse(BaseModel):
    id: int
    user_id: int
    title: str
    message: str
    type: str
    is_read: bool
    created_at: datetime

    model_config = {
        "from_attributes": True
    }