from .schemas import Event

# --- in memory storage (for learning) --- 
#                       sid 
EVENTS_BY_SESSION: dict[str, list[Event]] = {}
#              sid, info
SESSIONS: dict[str, dict] = {}