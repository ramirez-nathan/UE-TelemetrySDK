from fastapi import APIRouter, Depends, HTTPException, Query
from datetime import datetime, timezone
import uuid

from ..auth import require_api_key
from ..schemas import StartSessionIn, StartSessionOut, EndSession
from ..storage import EVENTS_BY_SESSION, SESSIONS

router = APIRouter(
    prefix="/sessions",
    tags=["sessions"],
    dependencies=[Depends(require_api_key)], # applies to ALL routes here
)

# parameters: StartSessionIn 
# response_model: StartSessionOut (json)
# --- Function ---
    # create sid using uuid
    # initialize SESSIONS @ sid with all ids & ts (dict in json)
        # ts - datetime.now(timezone.utc).isoformat()
    # intiialize EVENTS @ sid 
@router.post("/start", response_model=StartSessionOut)
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
    return StartSessionOut(session_id=sid)

# End Session Function
# parameters: StartSessionOut
# response_type: None
# --- Function ---
    # fill out the ended_at timestamp in SESSIONS[sid]
        # throw 404 if sid not found
@router.post("/end")
def end_session(body: EndSession):
    session = SESSIONS.get(body.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if SESSIONS[body.session_id]["ended_at"] is not None:
        raise HTTPException(status_code=409, detail="Session already ended")
    
    session["ended_at"] = datetime.now(timezone.utc).isoformat()
    return {"ended": True}

# Sessions List Function
# parameters: limit: int, active_only: bool (active sessions only)
# response model: Any
# --- Function ---
    # collect sessions list(SESSIONS.values())
    # if active_only, only include those where ended_at is None
    # sort by created_at descending (newest first)
    # return the first 'limit'
@router.get("")
def list_sessions(
    limit: int = Query(50, ge=1, le=200),
    active_only : bool = False
):
    sessions = list(SESSIONS.values())
    if active_only:
        sessions = [s for s in sessions if s["ended_at"] is None]
    
    sessions.sort(key=lambda s: s["created_at"], reverse=True)
    return {"sessions": sessions[:limit]}
        
