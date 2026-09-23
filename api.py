from fastapi import FastAPI
from pydantic import BaseModel
import hashlib
import json

from deduplicator import Deduplicator

app = FastAPI()

deduplicator = Deduplicator(ttl=60)


class Event(BaseModel):
    user_id: int
    action: str


@app.post("/events")
def process_event(event: Event):
    event_data = json.dumps(event.model_dump(), sort_keys=True)
    fingerprint = hashlib.sha256(event_data.encode()).hexdigest()

    result = deduplicator.check(fingerprint)

    return {
        "fingerprint": fingerprint,
        **result
    }


@app.get("/stats")
def get_stats():
    return deduplicator.stats()