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

from app.utils.token import verify_token


router = APIRouter()


async def close_policy_violation(
    websocket: WebSocket,
):
    try:
        await websocket.close(
            code=1008
        )
    except Exception:
        pass


@router.websocket(
    "/ws/notifications/{user_id}"
)
async def notification_websocket(
    websocket: WebSocket,
    user_id: int,
):
    db = SessionLocal()

    connected = False

    try:
        token = (
            websocket.query_params.get(
                "token"
            )
        )

        if not token:
            await close_policy_violation(
                websocket
            )
            return

        payload = verify_token(
            token
        )

        if payload is None:
            await close_policy_violation(
                websocket
            )
            return

        token_user_id = payload.get(
            "sub"
        )

        if token_user_id is None:
            await close_policy_violation(
                websocket
            )
            return

        try:
            token_user_id = int(
                token_user_id
            )
        except (
            TypeError,
            ValueError,
        ):
            await close_policy_violation(
                websocket
            )
            return

        if token_user_id != user_id:
            await close_policy_violation(
                websocket
            )
            return

        user = (
            db.query(User)
            .filter(
                User.id == user_id
            )
            .first()
        )

        if (
            not user
            or not user.is_active
        ):
            await close_policy_violation(
                websocket
            )
            return

        connection_count = (
            await notification_manager.connect(
                user_id,
                websocket,
            )
        )

        connected = True

        await websocket.send_json(
            {
                "type": "connection",
                "message": (
                    "Notification WebSocket connected"
                ),
                "user_id": user_id,
                "active_connections": (
                    connection_count
                ),
            }
        )

        while True:
            data = (
                await websocket.receive_json()
            )

            action = data.get(
                "action"
            )

            if action == "ping":
                await websocket.send_json(
                    {
                        "type": "pong",
                        "user_id": user_id,
                    }
                )

            elif action == "status":
                await websocket.send_json(
                    {
                        "type": (
                            "connection_status"
                        ),
                        "user_id": user_id,
                        "active_connections": (
                            notification_manager
                            .connection_count(
                                user_id
                            )
                        ),
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
        pass

    except Exception:
        if connected:
            try:
                await websocket.close(
                    code=1011
                )
            except Exception:
                pass

    finally:
        if connected:
            notification_manager.disconnect(
                user_id,
                websocket,
            )

        db.close()
