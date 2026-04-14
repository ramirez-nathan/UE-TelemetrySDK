from fastapi import APIRouter, Depends, HTTPException, Query

from ..auth import require_api_key
from ..schemas import EventBatch
from ..storage import EVENTS_BY_SESSION, SESSIONS

router = APIRouter(
    target = ["events"],
    dependencies=[Depends(require_api_key)], # applies to ALL routes here
)

# Add an Event(s) Function
# parameters: Eventbatch
# response_model: None (json)
# --- Function --- 
    # extend batch's events to EVENTS_BY_SESSION
        # throw 404 if session_id DNE
        # Pydantic e.model_dump() converts BaseModels into dicts
            # for ex it returns {"id": 123, "ts": 1700, "payload": {amount: 12}}
@router.post("/sessions/{session_id}/events")
def post_events(session_id: str, batch: EventBatch):
    if session_id not in SESSIONS:
        raise HTTPException(status_code=404, detail = "Session not found")
    if SESSIONS[session_id]["ended_at"] is not None:
        raise HTTPException(status_code=409, detail = "Session already ended")
    
    # store event objects by extending list
    EVENTS_BY_SESSION[session_id].extend(batch.events)
    return {"accepted": len(batch.events)}


# Timeline of EventsFunction
# parameters: session_id str, limit int = (Query of 50, 1<=limit<=200)
# response type: None
# --- Function ---
# get events from EVENTS_BY_SESSION @ session_id
# return the first limit(50) 
@router.get("/sessions/{session_id}/events")
def get_event_timeline(
    session_id: str, 
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    type: str | None = None,
):
    if session_id not in SESSIONS:
        raise HTTPException(status_code=404, detail = "Session not found")
    
    # return the first 50 events
    events = EVENTS_BY_SESSION.get(session_id, [])
    
    if type is not None:
        events = [e for e in events if e.type == type]
    page = events[offset : offset + limit]
    
    return {"session_id": session_id, 
            "offset": offset,
            "limit": limit,
            "total": len(events),
            "events": [e.model_dump() for e in page]
    }
