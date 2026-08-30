from pydantic import (
    BaseModel,
    Field,
)


class ChatSummaryResponse(BaseModel):
    chat_type: str
    chat_id: int
    message_count: int
    summary: str
    participants: list[int]


class ActionItem(BaseModel):
    message_id: int
    sender_id: int
    content: str


class ActionItemsResponse(BaseModel):
    chat_type: str
    chat_id: int
    action_items: list[ActionItem]


class ImportantMessage(BaseModel):
    message_id: int
    sender_id: int
    content: str
    importance_score: int


class ImportantMessagesResponse(BaseModel):
    chat_type: str
    chat_id: int
    messages: list[ImportantMessage]


class SmartReplyRequest(BaseModel):
    chat_type: str
    chat_id: int
    max_suggestions: int = Field(
        default=3,
        ge=1,
        le=5,
    )


class SmartReplyResponse(BaseModel):
    chat_type: str
    chat_id: int
    suggestions: list[str]
