from datetime import datetime
import enum
from pydantic import BaseModel
from uuid import UUID


class Sender(enum.Enum):
    user = "user"
    assistant = "assistant"


class StartChat(BaseModel):
    chat_id: UUID
    created_at: datetime
    message: str | None = None

class SendMessage(BaseModel):
    message: str


class MessageResponse(BaseModel):
    message_id: UUID
    sender: Sender
    content: str
    created_at: datetime


class ChatResponse(BaseModel):
    chat_id: UUID
    created_at: datetime
    messages: list[MessageResponse]