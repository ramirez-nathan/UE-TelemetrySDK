from fastapi import FastAPI
from .api import sessions, events

app = FastAPI(title = "Telemetry Replay API")

app.include_router(sessions.router)
app.include_router(events.router)