from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..models import Message, Ticket, User
from ..schemas import MessageOut, MessageCreate, MessageUpdate
from ..deps import get_db, get_current_user

router = APIRouter(prefix="/tickets/{ticket_id}/messages", tags=["messages"])

@router.post("", response_model=MessageOut)
def create_message(ticket_id: int, payload: MessageCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    ticket = db.get(Ticket, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket no encontrado")
    if user.role != "admin" and ticket.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No autorizado")
    msg = Message(ticket_id=ticket.id, sender_id=user.id, body=payload.body)
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg

@router.get("", response_model=list[MessageOut])
def list_messages(ticket_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    ticket = db.get(Ticket, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket no encontrado")
    if user.role != "admin" and ticket.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No autorizado")
    return db.query(Message).filter(Message.ticket_id == ticket.id).order_by(Message.created_at.asc()).all()

@router.patch("/{message_id}", response_model=MessageOut)
def update_message(ticket_id: int, message_id: int, payload: MessageUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    ticket = db.get(Ticket, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket no encontrado")
    msg = db.get(Message, message_id)
    if not msg or msg.ticket_id != ticket.id:
        raise HTTPException(status_code=404, detail="Mensaje no encontrado")
    if user.role != "admin" and ticket.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No autorizado")
    if payload.body is not None:
        msg.body = payload.body
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg

@router.delete("/{message_id}")
def delete_message(ticket_id: int, message_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    ticket = db.get(Ticket, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket no encontrado")
    msg = db.get(Message, message_id)
    if not msg or msg.ticket_id != ticket.id:
        raise HTTPException(status_code=404, detail="Mensaje no encontrado")
    if user.role != "admin" and ticket.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No autorizado")
    db.delete(msg)
    db.commit()
    return {"deleted": True, "message_id": message_id}