from pydantic import BaseModel, Field
from typing import Any


# ------- models --------
class StartSessionIn(BaseModel):
    build_version: str=Field(min_length=1)
    client_id: str | None = None

class StartSessionOut(BaseModel):
    session_id : str
class EndSession(BaseModel):
    session_id : str

class Event(BaseModel):
    type: str = Field(min_length=1, max_length=64)
    ts: int # timestamp in unix ms
    payload: dict[str, Any] = Field(default_factory=dict)

class EventBatch(BaseModel):
    events: list[Event] = Field(min_length=1, max_length=5000)
