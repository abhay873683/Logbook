from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.core.database import SessionLocal
from app.core.websocket.manager import manager

from app.models.user import User
from app.models.chat import (
    ChannelMember,
    GroupMember,
    DirectMessage,
    Message,
)


router = APIRouter()


def get_user(db, user_id: int):
    return (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )


def validate_room_access(
    db,
    user_id: int,
    room_id: str,
):
    if "_" not in room_id:
        return False

    room_type, room_value = room_id.split("_", 1)

    try:
        chat_id = int(room_value)
    except ValueError:
        return False

    if room_type == "channel":
        return (
            db.query(ChannelMember)
            .filter(
                ChannelMember.channel_id == chat_id,
                ChannelMember.user_id == user_id,
            )
            .first()
            is not None
        )

    if room_type == "group":
        return (
            db.query(GroupMember)
            .filter(
                GroupMember.group_id == chat_id,
                GroupMember.user_id == user_id,
            )
            .first()
            is not None
        )

    if room_type == "direct":
        conversation = (
            db.query(DirectMessage)
            .filter(DirectMessage.id == chat_id)
            .first()
        )

        if not conversation:
            return False

        return user_id in {
            conversation.user1_id,
            conversation.user2_id,
        }

    return False


@router.websocket("/ws/chat/{user_id}")
async def websocket_chat(
    websocket: WebSocket,
    user_id: int,
):
    db = SessionLocal()

    try:
        user = get_user(db, user_id)

        if not user:
            await websocket.close(code=1008)
            return

        await manager.connect(
            user_id,
            websocket,
        )

        await manager.send_personal_message(
            user_id,
            {
                "type": "connection",
                "message": "WebSocket connected",
                "user_id": user_id,
            },
        )

        while True:
            data = await websocket.receive_json()

            action = data.get("action")

            if action == "join_room":
                room_id = str(data.get("room_id", ""))

                if not validate_room_access(
                    db,
                    user_id,
                    room_id,
                ):
                    await manager.send_personal_message(
                        user_id,
                        {
                            "type": "error",
                            "message": "Invalid room or access denied",
                        },
                    )
                    continue

                manager.join_room(
                    user_id,
                    room_id,
                )

                await manager.broadcast(
                    room_id,
                    {
                        "type": "room_join",
                        "room_id": room_id,
                        "user_id": user_id,
                    },
                )

            elif action == "leave_room":
                room_id = str(data.get("room_id", ""))

                manager.leave_room(
                    user_id,
                    room_id,
                )

                await manager.send_personal_message(
                    user_id,
                    {
                        "type": "room_leave",
                        "room_id": room_id,
                    },
                )

            elif action == "send_message":
                room_id = str(data.get("room_id", ""))
                content = str(data.get("message", "")).strip()

                if not content:
                    await manager.send_personal_message(
                        user_id,
                        {
                            "type": "error",
                            "message": "Message cannot be empty",
                        },
                    )
                    continue

                if not manager.is_room_member(
                    user_id,
                    room_id,
                ):
                    await manager.send_personal_message(
                        user_id,
                        {
                            "type": "error",
                            "message": "Join the room before sending messages",
                        },
                    )
                    continue

                room_type, room_value = room_id.split("_", 1)
                chat_id = int(room_value)

                message = Message(
                    chat_type=room_type,
                    chat_id=chat_id,
                    sender_id=user_id,
                    content=content,
                    file_url=None,
                    is_read=False,
                )

                db.add(message)
                db.commit()
                db.refresh(message)

                await manager.broadcast(
                    room_id,
                    {
                        "type": "message",
                        "message_id": message.id,
                        "room_id": room_id,
                        "sender_id": user_id,
                        "content": message.content,
                        "created_at": (
                            message.created_at.isoformat()
                            if message.created_at
                            else None
                        ),
                    },
                )

            elif action == "typing":
                room_id = str(data.get("room_id", ""))

                if manager.is_room_member(
                    user_id,
                    room_id,
                ):
                    await manager.broadcast(
                        room_id,
                        {
                            "type": "typing",
                            "room_id": room_id,
                            "user_id": user_id,
                            "is_typing": bool(
                                data.get("is_typing", True)
                            ),
                        },
                    )

            else:
                await manager.send_personal_message(
                    user_id,
                    {
                        "type": "error",
                        "message": "Invalid WebSocket action",
                    },
                )

    except WebSocketDisconnect:
        manager.disconnect(user_id)

    except Exception:
        manager.disconnect(user_id)

        try:
            await websocket.close(code=1011)
        except Exception:
            pass

    finally:
        db.close()