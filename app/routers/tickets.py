from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..models import Ticket, User
from ..schemas import TicketCreate, TicketOut, TicketUpdate
from ..deps import get_db, get_current_user

router = APIRouter(prefix="/tickets", tags=["tickets"])

@router.post("", response_model=TicketOut)
def create_ticket(payload: TicketCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    # Asegurar valores no nulos explícitos para SQLite y evitar dependencias de defaults
    priority = payload.priority or "normal"
    ticket = Ticket(user_id=user.id, title=payload.title, description=payload.description, priority=priority, status="open")
    try:
        db.add(ticket)
        db.commit()
        db.refresh(ticket)
        return ticket
    except Exception as e:
        db.rollback()
        # Propagar detalle para diagnóstico rápido en desarrollo
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail=f"DB error: {e}")

@router.get("", response_model=list[TicketOut])
def list_tickets(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    q = db.query(Ticket)
    if user.role != "admin":
        q = q.filter(Ticket.user_id == user.id)
    return q.order_by(Ticket.updated_at.desc()).all()

@router.patch("/{ticket_id}", response_model=TicketOut)
def update_ticket(ticket_id: int, payload: TicketUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    ticket = db.get(Ticket, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket no encontrado")
    if user.role != "admin" and ticket.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No autorizado")
    # aplicar cambios parciales
    if payload.title is not None:
        ticket.title = payload.title
    if payload.description is not None:
        ticket.description = payload.description
    if payload.status is not None:
        ticket.status = payload.status
    if payload.priority is not None:
        ticket.priority = payload.priority or "normal"
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket

@router.delete("/{ticket_id}")
def delete_ticket(ticket_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    ticket = db.get(Ticket, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket no encontrado")
    if user.role != "admin" and ticket.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No autorizado")
    db.delete(ticket)
    db.commit()
    return {"deleted": True, "ticket_id": ticket_id}