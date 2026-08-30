from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    field_validator,
)


class MessageReactionCreate(BaseModel):
    reaction: str

    @field_validator("reaction")
    @classmethod
    def validate_reaction(cls, value):
        value = value.strip()

        if not value:
            raise ValueError(
                "Reaction cannot be empty"
            )

        if len(value) > 50:
            raise ValueError(
                "Reaction is too long"
            )

        return value


class MessageReactionResponse(BaseModel):
    id: int
    message_id: int
    user_id: int
    reaction: str
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


class MessageReactionDeleteResponse(BaseModel):
    message: str
