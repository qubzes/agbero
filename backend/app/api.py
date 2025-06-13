from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from langchain_core.messages import (
    AIMessage,
    HumanMessage,
    SystemMessage,
    trim_messages,
)
from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
)
from langchain_groq import ChatGroq
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Chat, Message
from app.schemas import ChatResponse, MessageResponse, SendMessage, StartChat
from app.settings import Settings

router = APIRouter(prefix="/chats", tags=["Chats"])

settings = Settings()

groq_api_key = settings.GROQ_API_KEY
model = settings.GROQ_MODEL
groq_chat = ChatGroq(groq_api_key=groq_api_key, model_name=model)


prompt = ChatPromptTemplate.from_messages(
    [
        SystemMessage(content=settings.SYSTEM_PROMPT),
        MessagesPlaceholder(variable_name="chat_history"),
        HumanMessagePromptTemplate.from_template("{human_input}"),
    ]
)


@router.get("")
async def get_all_chats(db: Session = Depends(get_db)) -> List[StartChat]:
    """Get all chats."""
    try:
        chats: List[Chat] = Chat.list(db)
        return [
            StartChat(chat_id=chat.id, created_at=chat.created_at.isoformat())
            for chat in chats
        ]
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to retrieve chats: {str(e)}"
        )


@router.post("")
async def start_new_chat(db: Session = Depends(get_db)) -> StartChat:
    """Create a new chat."""
    try:
        chat = Chat()
        chat.save(db)

        chain = prompt | groq_chat
        response = chain.invoke(
            {"chat_history": [], "human_input": "Start a conversation"}
        )

        message = Message(
            chat_id=chat.id, sender="assistant", content=response.content
        )
        message.save(db)

        return StartChat(
            chat_id=chat.id,
            message=message.content,
            created_at=chat.created_at.isoformat(),
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to create new chat: {str(e)}"
        )


@router.get("/{chat_id}")
async def get_chat(
    chat_id: UUID, db: Session = Depends(get_db)
) -> ChatResponse:
    """Get a specific chat and its messages."""
    try:
        chat: Chat = Chat.get(db, chat_id)
        if not chat:
            raise HTTPException(status_code=404, detail="Chat not found")

        messages: List[Message] = Message.list(
            db, chat_id=chat.id, sort_by="created_at"
        )
        return ChatResponse(
            chat_id=chat.id,
            created_at=chat.created_at.isoformat(),
            messages=[
                MessageResponse(
                    message_id=message.id,
                    sender=message.sender,
                    content=message.content,
                    created_at=message.created_at.isoformat(),
                )
                for message in messages
            ],
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to retrieve chat: {str(e)}"
        )


@router.delete("/{chat_id}")
async def delete_chat(chat_id: UUID, db: Session = Depends(get_db)) -> str:
    """Delete a specific chat and its messages."""
    try:
        chat: Chat = Chat.get(db, chat_id)
        if not chat:
            raise HTTPException(status_code=404, detail="Chat not found")

        messages: List[Message] = Message.list(db, chat_id=chat.id)
        for msg in messages:
            msg.delete(db)

        chat.delete(db)
        return "Chat and its messages deleted successfully"
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete chat and its messages: {str(e)}",
        )


@router.post("/{chat_id}/message")
async def send_message_to_chat(
    chat_id: UUID, message: SendMessage, db: Session = Depends(get_db)
) -> MessageResponse:
    """Send a message to a chat."""
    try:
        chat: Chat = Chat.get(db, chat_id)
        if not chat:
            raise HTTPException(status_code=404, detail="Chat not found")

        # Save the user message
        user_message = Message(
            chat_id=chat.id, sender="user", content=message.message
        )
        user_message.save(db)

        # Retrieve chat history
        messages = Message.list(db, chat_id=chat.id, sort_by="created_at")
        chat_history = []
        for msg in messages:
            if msg.sender == "user":
                chat_history.append(HumanMessage(content=msg.content))
            else:
                chat_history.append(AIMessage(content=msg.content))

        # Trim the chat history
        messages_to_send = trim_messages(
            chat_history,
            max_tokens=256,
            token_counter=lambda messages: sum(
                len(msg.content.split()) for msg in messages
            ),
            strategy="last",
            include_system=True,
            allow_partial=False,
        )

        # Generate the response
        chain = prompt | groq_chat
        response = chain.invoke(
            {"chat_history": messages_to_send, "human_input": message.message}
        )

        # Save the assistant's response
        ai_message = Message(
            chat_id=chat.id, sender="assistant", content=response.content
        )
        ai_message.save(db)

        return MessageResponse(
            message_id=ai_message.id,
            chat_id=chat.id,
            sender="assistant",
            content=response.content,
            created_at=ai_message.created_at.isoformat(),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
