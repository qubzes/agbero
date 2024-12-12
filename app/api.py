from typing import List
from uuid import UUID
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.settings import Settings
from app.database import get_db
from app.models import Thread, Message
from app.schemas import SendMessage, ThreadResponse, MessageResponse
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

router = APIRouter(prefix="/chat", tags=["Chat"])

setting = Settings()

# Initialize Groq Chat
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
async def get_all_threads(db: Session = Depends(get_db)):
    """Get all chat threads."""
    try:
        threads: List[Thread] = Thread.list(db)
        return [
            ThreadResponse(
                thread_id=thread.id, created_at=thread.created_at.isoformat()
            )
            for thread in threads
        ]
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to retrieve chat threads: {str(e)}"
        )


@router.post("/")
async def create_thread(db: Session = Depends(get_db)):
    """Create a new chat thread."""
    try:
        thread = Thread()
        thread.save(db)
        return ThreadResponse(
            thread_id=thread.id, created_at=thread.created_at.isoformat()
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to create chat thread: {str(e)}"
        )


@router.get("/{thread_id}")
async def get_thread(thread_id: UUID, db: Session = Depends(get_db)):
    """Get a specific chat thread with messages."""
    try:
        thread: Thread = Thread.get(db, thread_id)
        if not thread:
            raise HTTPException(status_code=404, detail="Thread not found")

        messages: List[Message] = Message.list(
            db, thread_id=thread.id, sort_by="created_at"
        )
        return {
            "thread": ThreadResponse(
                thread_id=thread.id, created_at=thread.created_at.isoformat()
            ),
            "messages": [
                MessageResponse(
                    message_id=msg.id,
                    thread_id=msg.thread_id,
                    sender=msg.sender,
                    content=msg.content,
                    created_at=msg.created_at.isoformat(),
                )
                for msg in messages
            ],
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to retrieve chat thread: {str(e)}"
        )


@router.delete("/{thread_id}")
async def delete_thread(thread_id: UUID, db: Session = Depends(get_db)):
    """Delete a specific chat thread and its messages."""
    try:
        thread: Thread = Thread.get(db, thread_id)
        if not thread:
            raise HTTPException(status_code=404, detail="Thread not found")

        # Delete all messages associated with the thread
        messages: List[Message] = Message.list(db, thread_id=thread.id)
        for msg in messages:
            msg.delete(db)

        # Delete the thread
        thread.delete(db)
        return {"detail": "Thread and its messages deleted successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete chat thread and its messages: {str(e)}",
        )


@router.post("/{thread_id}/message")
async def send_message_to_thread(
    thread_id: UUID, message: SendMessage, db: Session = Depends(get_db)
) -> MessageResponse:
    """Send a message to a specific thread and get a response from the chatbot."""
    try:
        thread: Thread = Thread.get(db, thread_id)
        if not thread:
            raise HTTPException(status_code=404, detail="Thread not found")

        # Save the user message
        user_message = Message(
            thread_id=thread.id, sender="user", content=message.message
        )
        user_message.save(db)

        # Retrieve chat history
        messages = Message.list(db, thread_id=thread.id, sort_by="created_at")
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
            thread_id=thread.id, sender="assistant", content=response.content
        )
        ai_message.save(db)

        return MessageResponse(
            message_id=ai_message.id,
            thread_id=thread.id,
            sender="assistant",
            content=response.content,
            created_at=ai_message.created_at.isoformat(),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
