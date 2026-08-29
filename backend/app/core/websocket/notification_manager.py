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
            self.active_connections[
                user_id
            ] = set()

        self.active_connections[
            user_id
        ].add(
            websocket
        )

        return self.connection_count(
            user_id
        )

    def disconnect(
        self,
        user_id: int,
        websocket: WebSocket,
    ):
        connections = (
            self.active_connections.get(
                user_id
            )
        )

        if not connections:
            return

        connections.discard(
            websocket
        )

        if not connections:
            self.active_connections.pop(
                user_id,
                None,
            )

    def connection_count(
        self,
        user_id: int,
    ) -> int:
        return len(
            self.active_connections.get(
                user_id,
                set(),
            )
        )

    def is_connected(
        self,
        user_id: int,
    ) -> bool:
        return (
            self.connection_count(user_id)
            > 0
        )

    def connected_user_count(
        self,
    ) -> int:
        return len(
            self.active_connections
        )

    async def send_to_user(
        self,
        user_id: int,
        data: dict,
    ) -> int:
        connections = (
            self.active_connections.get(
                user_id,
                set(),
            ).copy()
        )

        disconnected = []
        sent_count = 0

        for websocket in connections:
            try:
                await websocket.send_json(
                    data
                )
                sent_count += 1

            except Exception:
                disconnected.append(
                    websocket
                )

        for websocket in disconnected:
            self.disconnect(
                user_id,
                websocket,
            )

        return sent_count


notification_manager = (
    NotificationConnectionManager()
)
