from typing import List
from uuid import UUID
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.settings import Settings
from app.database import get_db
from app.models import Chat, Message
from app.schemas import SendMessage, StartChat, MessageResponse, ChatResponse
from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
)
from langchain_core.messages import (
    SystemMessage,
    HumanMessage,
    AIMessage,
    trim_messages,
)
from langchain_groq import ChatGroq

router = APIRouter(prefix="/chats", tags=["Chats"])

setting = Settings()

groq_api_key = setting.GROQ_API_KEY
model = "llama-3.3-70b-versatile"
groq_chat = ChatGroq(groq_api_key=groq_api_key, model_name=model)

system_prompt = (
    "From now on, you be rugged Warri ghetto boy, coded like high naja cultist. "
    "Your talk go strong, deep, and rare pidgin, filled with cultist slangs, street "
    "charge, and rugged cult vibes. No dey yarn soft or gentle; all your words must carry "
    "authority and be laced with underground language wey street boys dey flow. Make "
    "sure every sentence rugged, no lele. If your words no be strong pidgin or cultist "
    "lingo, your matter go cast and you go collect woto woto. Speak as if na you be "
    "boss for street council. Remember, na senior man wey you be, so always show charge "
    "and dominance in your tone."
    "No normal English go show for your talk"
    "Keep your response very short and sharp unless the situation demand medium or long talk."
)

prompt = ChatPromptTemplate.from_messages(
    [
        SystemMessage(content=system_prompt),
        MessagesPlaceholder(variable_name="chat_history"),
        HumanMessagePromptTemplate.from_template("{human_input}"),
    ]
)


@router.get("/")
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


@router.post("/")
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
            id=chat.id,
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
            max_tokens=2048,
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
