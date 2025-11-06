from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class AdminUserCreate(BaseModel):
    email: EmailStr
    password: str
    role: Optional[str] = "user"

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    email: EmailStr
    role: str
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TicketCreate(BaseModel):
    title: str
    description: str
    priority: Optional[str] = "normal"

class TicketUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None

class TicketOut(BaseModel):
    id: int
    title: str
    description: str
    status: str
    priority: str
    user_id: int
    class Config:
        from_attributes = True

class MessageOut(BaseModel):
    id: int
    ticket_id: int
    sender_id: Optional[int]
    body: str
    created_at: datetime
    class Config:
        from_attributes = True

class MessageCreate(BaseModel):
    body: str

class MessageUpdate(BaseModel):
    body: Optional[str] = None

class UserUpdate(BaseModel):
    role: Optional[str] = None
    password: Optional[str] = None