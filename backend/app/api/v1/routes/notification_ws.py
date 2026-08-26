from fastapi import (
    APIRouter,
    WebSocket,
    WebSocketDisconnect,
)

from app.core.database import SessionLocal

from app.core.websocket.notification_manager import (
    notification_manager,
)

from app.models.user import User


router = APIRouter()


@router.websocket(
    "/ws/notifications/{user_id}"
)
async def notification_websocket(
    websocket: WebSocket,
    user_id: int,
):
    db = SessionLocal()

    try:
        user = (
            db.query(User)
            .filter(User.id == user_id)
            .first()
        )

        if not user:
            await websocket.close(
                code=1008
            )
            return

        await notification_manager.connect(
            user_id,
            websocket,
        )

        await notification_manager.send_to_user(
            user_id,
            {
                "type": "connection",
                "message": (
                    "Notification WebSocket connected"
                ),
                "user_id": user_id,
            },
        )

        while True:
            data = await websocket.receive_json()

            action = data.get("action")

            if action == "ping":
                await websocket.send_json(
                    {
                        "type": "pong"
                    }
                )

            else:
                await websocket.send_json(
                    {
                        "type": "error",
                        "message": (
                            "Invalid notification "
                            "WebSocket action"
                        ),
                    }
                )

    except WebSocketDisconnect:
        notification_manager.disconnect(
            user_id,
            websocket,
        )

    except Exception:
        notification_manager.disconnect(
            user_id,
            websocket,
        )

        try:
            await websocket.close(
                code=1011
            )
        except Exception:
            pass

    finally:
        db.close()