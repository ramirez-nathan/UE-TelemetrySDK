from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
app = FastAPI()
class Item(BaseModel):
    name: str
    price: float
    is_offer: bool | None = None
class EventIn(BaseModel):
    name: str
    timestamp: datetime

class EventOut(EventIn):
    id: int
@app.get("/")
def read_root():
    return {"Hello": "World"}
@app.get("/health")
def health():
    return {"ok": True}
