from fastapi import FastAPI, Query, HTTPException
from datetime import datetime, timezone
from pydantic import BaseModel, Field
from typing import Any
import uuid

# ------- models --------
class StartSessionIn(BaseModel):
    build_version: str=Field(min_length=1)
    client_id: str | None = None

class EndSessionIn(BaseModel):
    session_id : str

class EndSessionOut(BaseModel):
    session_id : str

class Event(BaseModel):
    type: str = Field(min_length=1, max_length=64)
    ts: int # timestamp in unix ms
    payload: dict[str, Any] = Field(default_factory=dict)

class EventBatch(BaseModel):
    events: list[Event] = Field(min_length=1, max_length=5000)

# --- in memory storage (for learning) --- 
#                       sid 
EVENTS_BY_SESSION: dict[str, list[Event]] = {}
#              sid, info
SESSIONS: dict[str, dict] = {}

app = FastAPI()

# parameters: StartSessionIn 
# response_model: StartSessionOut (json)
# --- Function ---
    # create sid using uuid
    # initialize SESSIONS @ sid with all ids & ts (dict in json)
        # ts - datetime.now(timezone.utc).isoformat()
    # intiialize EVENTS @ sid 
@app.post("/sessions/start", response_model=EndSessionIn)
def start_session(body: StartSessionIn):
    sid = str(uuid.uuid4())
    SESSIONS[sid] = {
        "session_id": sid,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "ended_at" : None,
        "build_version": body.build_version,
        "client_id": body.client_id
    }
    EVENTS_BY_SESSION[sid] = []
    return EndSessionIn(session_id=sid)

# End Session Function
# parameters: StartSessionOut
# response_type: None
# --- Function ---
    # fill out the ended_at timestamp in SESSIONS[sid]
        # throw 404 if sid not found
@app.post("/sessions/end")
def end_session(body: EndSessionIn):
    session = SESSIONS.get(body.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    session["ended_at"] = datetime.now(timezone.utc).isoformat()
    return {"Ended session": True}

# Sessions List Function
# parameters: limit: int, active_only: bool (active sessions only)
# response model: Any
# --- Function ---
    # collect sessions list(SESSIONS.values())
    # if active_only, only include those where ended_at is None
    # sort by created_at descending (newest first)
    # return the first 'limit'
@app.get("/sessions")
def list_sessions(
    limit: int = Query(50, ge=1, le=200),
    active_only : bool = False
):
    sessions = list(SESSIONS.values())
    if active_only is True:
        sessions = [s for s in sessions if s["ended_at"] is None]
    
    sessions.sort(key=lambda s: s["created_at"], reverse=True)
    return {"sessions": sessions[:limit]}
        

# Add an Event(s) Function
# parameters: Eventbatch
# response_model: None (json)
# --- Function --- 
    # extend batch's events to EVENTS_BY_SESSION
        # throw 404 if session_id DNE
        # Pydantic e.model_dump() converts BaseModels into dicts
            # for ex it returns {"id": 123, "ts": 1700, "payload": {amount: 12}}
@app.post("/sessions/{session_id}/events")
def post_events(session_id: str, batch: EventBatch):
    if session_id not in SESSIONS:
        raise HTTPException(status_code=404, detail = "Session not found")
    
    # store events as dicts using pydantic's e.model_dump()
    EVENTS_BY_SESSION[session_id].extend(batch.events)
    return {"accepted": len(batch.events)}


# Timeline of EventsFunction
# parameters: session_id str, limit int = (Query of 50, 1<=limit<=200)
# response type: None
# --- Function ---
# get events from EVENTS_BY_SESSION @ session_id
# return the first limit(50) 
@app.get("/sessions/{session_id}/events")
def get_event_timeline(
    session_id: str, 
    limit: int = Query(50, ge=1, le=200),
    type: str | None = None
):
    if session_id not in SESSIONS:
        raise HTTPException(status_code=404, detail = "Session not found")
    
    # return the first 50 events
    events = EVENTS_BY_SESSION.get(session_id, [])

    if type is not None:
        events = [e for e in events if e.type == type]
    
    return {"session_id": session_id, "events": [e.model_dump() for e in events[:limit]]}
