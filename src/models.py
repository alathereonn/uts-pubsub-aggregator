from pydantic import BaseModel, Field
from typing import Any, Dict, List, Annotated
from datetime import datetime

# Pydantic v2: tak perlu strip_whitespace utk test ini; hilangkan peringatan deprecated
Topic = Annotated[str, Field(min_length=1, max_length=200)]
EventID = Annotated[str, Field(min_length=1, max_length=200)]
Source  = Annotated[str, Field(min_length=1, max_length=200)]

class Event(BaseModel):
    topic: Topic
    event_id: EventID
    timestamp: datetime
    source: Source
    payload: Dict[str, Any]

class PublishRequest(BaseModel):
    events: List[Event]
