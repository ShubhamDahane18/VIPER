from typing import Optional, List
from datetime import datetime
from sqlmodel import Field, SQLModel, create_engine
import os

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)
    role: str = Field(default="engineering") # admin, legal, engineering, sales
    
class Meeting(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    startTime: datetime = Field(default_factory=datetime.utcnow)
    device_serial: str = Field(default="HR191-000")
    allowed_roles: str = Field(default="admin") # Comma separated for MVP sqlite
    audio_file_path: Optional[str] = None
    transcript_redacted_path: Optional[str] = None
    
    # Audit trail
    uploaded_by_user_id: Optional[int] = Field(default=None, foreign_key="user.id")

class AuditLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    action: str # "login", "audio access", "RAG query", "access denied", "device transfer"
    entity: Optional[str] = None
    description: Optional[str] = None

class ActionItem(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    meeting_id: Optional[int] = Field(default=None, foreign_key="meeting.id")
    task_description: str
    owner: Optional[str] = None
    deadline: Optional[str] = None
    status: str = Field(default="PENDING APPROVAL") # PENDING APPROVAL, APPROVED, REJECTED
