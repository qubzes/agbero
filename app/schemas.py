from datetime import datetime
import enum
from pydantic import BaseModel
from uuid import UUID


class Sender(enum.Enum):
    user = "user"
    assistant = "assistant"


class SendMessage(BaseModel):
    message: str


class ThreadResponse(BaseModel):
    thread_id: UUID
    created_at: datetime


class MessageResponse(BaseModel):
    message_id: UUID
    thread_id: UUID
    sender: Sender
    content: str
    created_at: datetime
