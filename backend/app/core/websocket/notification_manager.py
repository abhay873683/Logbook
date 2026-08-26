from fastapi import WebSocket


class NotificationConnectionManager:

    def __init__(self):
        self.active_connections: dict[
            int,
            set[WebSocket],
        ] = {}

    async def connect(
        self,
        user_id: int,
        websocket: WebSocket,
    ):
        await websocket.accept()

        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()

        self.active_connections[user_id].add(
            websocket
        )

    def disconnect(
        self,
        user_id: int,
        websocket: WebSocket,
    ):
        connections = (
            self.active_connections.get(user_id)
        )

        if not connections:
            return

        connections.discard(websocket)

        if not connections:
            self.active_connections.pop(
                user_id,
                None,
            )

    async def send_to_user(
        self,
        user_id: int,
        data: dict,
    ):
        connections = (
            self.active_connections.get(
                user_id,
                set(),
            ).copy()
        )

        disconnected = []

        for websocket in connections:
            try:
                await websocket.send_json(data)

            except Exception:
                disconnected.append(websocket)

        for websocket in disconnected:
            self.disconnect(
                user_id,
                websocket,
            )


notification_manager = (
    NotificationConnectionManager()
)