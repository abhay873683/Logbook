from typing import Any

from pydantic import BaseModel


class NotificationChannelResult(BaseModel):
    channel: str
    delivered: bool
    reason: str
    provider: str | None = None


class NotificationDeliveryResponse(BaseModel):
    notification_id: int
    user_id: int
    delivered_channels: int
    channels: dict[str, Any]
