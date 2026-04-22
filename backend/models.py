from datetime import datetime
from typing import List, Optional, Dict
from sqlmodel import SQLModel, Field, Relationship
import uuid

class Session(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    title: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    messages: List["Message"] = Relationship(back_populates="session")

class Message(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    session_id: uuid.UUID = Field(foreign_key="session.id")
    role: str  # user, assistant, system, tool
    content: str
    metadata_info: Optional[str] = Field(default=None) # Store tokens, etc.
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    session: Optional[Session] = Relationship(back_populates="messages")

class UserMemory(SQLModel, table=True):
    key: str = Field(primary_key=True)
    value: str
    updated_at: datetime = Field(default_factory=datetime.utcnow)
