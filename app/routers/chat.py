import os
import jwt
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from ..db import SessionLocal
from ..models import Ticket, User

router = APIRouter(prefix="/ws", tags=["chat"])
SECRET_KEY = os.getenv("SECRET_KEY", "dev_secret_key_change_me")
ALGORITHM = "HS256"

@router.websocket("/chat/{ticket_id}")
async def chat_ws(websocket: WebSocket, ticket_id: int):
    await websocket.accept()
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=4401)
        return
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload.get("sub"))
        role = payload.get("role")
    except Exception:
        await websocket.close(code=4401)
        return

    session = SessionLocal()
    try:
        ticket = session.get(Ticket, ticket_id)
        user = session.get(User, user_id)
        if not ticket or not user:
            await websocket.close(code=4404)
            return
        if user.role != "admin" and ticket.user_id != user.id:
            await websocket.close(code=4403)
            return
    finally:
        session.close()

    try:
        while True:
            data = await websocket.receive_text()
            # Eco simple por ahora (persistencia se implementa después)
            await websocket.send_text(data)
    except WebSocketDisconnect:
        return