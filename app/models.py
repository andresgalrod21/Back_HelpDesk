from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.sql import func

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    __table_args__ = {"sqlite_autoincrement": True}
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(Text, nullable=False)
    role = Column(String(20), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    last_login = Column(DateTime(timezone=True), nullable=True)

    tickets = relationship("Ticket", back_populates="user")

class Ticket(Base):
    __tablename__ = "tickets"
    __table_args__ = {"sqlite_autoincrement": True}
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    status = Column(String(20), nullable=False, default="open")
    priority = Column(String(20), nullable=False, default="normal")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    user = relationship("User", back_populates="tickets")
    messages = relationship("Message", back_populates="ticket")

class Message(Base):
    __tablename__ = "messages"
    __table_args__ = {"sqlite_autoincrement": True}
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    ticket_id = Column(Integer, ForeignKey("tickets.id", ondelete="CASCADE"), nullable=False, index=True)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    body = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    ticket = relationship("Ticket", back_populates="messages")
    sender = relationship("User")