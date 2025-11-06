import os
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from .db import engine
from .models import Base
from .routers import auth, tickets, admin, chat, messages

app = FastAPI(title="HelpDeskCloud API")

# CORS: por defecto sin credenciales para permitir "*" en desarrollo.
# Si necesitas cookies/sesiones, establece CORS_ALLOW_CREDENTIALS=true
origins_env = os.getenv("CORS_ORIGINS", "*")
origins = [o.strip() for o in origins_env.split(",")] if origins_env else ["*"]
CORS_ALLOW_CREDENTIALS = os.getenv("CORS_ALLOW_CREDENTIALS", "false").lower() == "true"

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=CORS_ALLOW_CREDENTIALS,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    # No crear tablas automáticamente a menos que se habilite explícitamente por env
    if os.getenv("DB_CREATE_ON_STARTUP", "false").lower() == "true":
        Base.metadata.create_all(bind=engine)

@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/docs")

@app.get("/health")
def health():
    return {"status": "ok"}

app.include_router(auth.router)
app.include_router(tickets.router)
app.include_router(admin.router)
app.include_router(chat.router)
app.include_router(messages.router)