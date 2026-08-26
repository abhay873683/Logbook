from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[int, WebSocket] = {}
        self.rooms: dict[str, set[int]] = {}

    async def connect(
        self,
        user_id: int,
        websocket: WebSocket,
    ):
        await websocket.accept()
        self.active_connections[user_id] = websocket

    def disconnect(
        self,
        user_id: int,
    ):
        self.active_connections.pop(user_id, None)

        empty_rooms = []

        for room_id, members in self.rooms.items():
            members.discard(user_id)

            if not members:
                empty_rooms.append(room_id)

        for room_id in empty_rooms:
            self.rooms.pop(room_id, None)

    def join_room(
        self,
        user_id: int,
        room_id: str,
    ):
        if room_id not in self.rooms:
            self.rooms[room_id] = set()

        self.rooms[room_id].add(user_id)

    def leave_room(
        self,
        user_id: int,
        room_id: str,
    ):
        if room_id not in self.rooms:
            return

        self.rooms[room_id].discard(user_id)

        if not self.rooms[room_id]:
            self.rooms.pop(room_id, None)

    def is_room_member(
        self,
        user_id: int,
        room_id: str,
    ) -> bool:
        return (
            room_id in self.rooms
            and user_id in self.rooms[room_id]
        )

    async def send_personal_message(
        self,
        user_id: int,
        data: dict,
    ):
        websocket = self.active_connections.get(user_id)

        if websocket:
            await websocket.send_json(data)

    async def broadcast(
        self,
        room_id: str,
        data: dict,
    ):
        user_ids = self.rooms.get(room_id, set()).copy()

        disconnected_users = []

        for user_id in user_ids:
            websocket = self.active_connections.get(user_id)

            if not websocket:
                continue

            try:
                await websocket.send_json(data)

            except Exception:
                disconnected_users.append(user_id)

        for user_id in disconnected_users:
            self.disconnect(user_id)


manager = ConnectionManager()