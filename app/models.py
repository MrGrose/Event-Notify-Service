from enum import StrEnum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class EventType(StrEnum):
    TASK_CREATED = "task_created"
    MEETING_CREATED = "meeting_created"
    MESSAGE_RECEIVED = "message_received"


class EventPayload(BaseModel):
    title: str | None = None
    description: str | None = None
    text: str | None = None
    sender: str | None = None
    time: str | None = None


class EventRequest(BaseModel):
    event_id: UUID
    user_id: str = Field(min_length=1)
    type: EventType
    payload: EventPayload


class EventRecord(BaseModel):
    event_id: UUID
    user_id: str
    type: EventType
    payload: dict[str, Any]
    notification_text: str | None = None


class EventAcceptedResponse(BaseModel):
    status: str
    event_id: UUID
    detail: str


class EventRejectedResponse(BaseModel):
    status: str
    event_id: UUID
    detail: str
