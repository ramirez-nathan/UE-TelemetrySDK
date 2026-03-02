import os
import psycopg
from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime

DATABASE_URL = os.environ["DATABASE_URL"]

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

def init_db():
    with psycopg.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur: # a handle to run SQL and fetch results
            cur.execute(""" 
                CREATE TABLE IF NOT EXISTS events (
                    id BIGSERIAL PRIMARY KEY,
                    name TEXT NOT NULL,
                    ts TIMESTAMPTZ NOT NULL
                );
            """)
        conn.commit()
@app.on_event("startup")
def on_startup():
    init_db()
@app.get("/")
def read_root():
    return {"Hello": "World"}
@app.get("/health")
def health():
    return {"ok": True}
