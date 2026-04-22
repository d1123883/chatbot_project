from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select
from .database import engine, create_db_and_tables, get_session
from .models import Session as ChatSession, Message, UserMemory
from .orchestrator import AIAgent
import uuid

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
    session_id: uuid.UUID, 
    prompt: str, 
    db: Session = Depends(get_session)
):
    agent = AIAgent(db)
    return StreamingResponse(
        agent.generate_response(str(session_id), prompt), 
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
