import uuid
import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load environment variables using ABSOLUTE path relative to this file
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

from fastapi import FastAPI, Depends, HTTPException, Query, File, UploadFile, Form
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select
from .database import engine, create_db_and_tables, get_session
from .models import Session as ChatSession, Message, UserMemory
from .orchestrator import AIAgent

app = FastAPI(title="Advanced AI Chatbot")

# Enable CORS for frontend interaction
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

@app.post("/sessions", response_model=ChatSession)
def create_session(title: str, db: Session = Depends(get_session)):
    new_session = ChatSession(title=title)
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    return new_session

@app.get("/sessions")
def list_sessions(db: Session = Depends(get_session)):
    return db.exec(select(ChatSession)).all()

@app.get("/sessions/{session_id}/messages")
def get_messages(session_id: uuid.UUID, db: Session = Depends(get_session)):
    statement = select(Message).where(Message.session_id == session_id).order_by(Message.created_at)
    return db.exec(statement).all()

@app.post("/chat/stream")
async def chat_stream(
    session_id: uuid.UUID = Form(...), 
    prompt: str = Form(...), 
    file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_session)
):
    agent = AIAgent(db)
    file_data = None
    if file:
        file_data = {
            "mime_type": file.content_type,
            "data": await file.read()
        }
    return StreamingResponse(
        agent.generate_response(session_id, prompt, file_data), 
        media_type="text/event-stream"
    )

@app.post("/memory")
def update_memory(key: str, value: str, db: Session = Depends(get_session)):
    memory = db.get(UserMemory, key)
    if memory:
        memory.value = value
    else:
        memory = UserMemory(key=key, value=value)
    db.add(memory)
    db.commit()
    return {"status": "success"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
