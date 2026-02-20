from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID


class LearningPathCreate(BaseModel):
    title: str
    subject: str
    description: Optional[str] = None
    difficulty: Optional[str] = "debutant"
    total_sessions: Optional[int] = 5


class LearningPathResponse(BaseModel):
    id: UUID
    user_id: UUID
    title: str
    description: Optional[str]
    subject: str
    difficulty: str
    total_sessions: int
    completed_sessions: int
    progress_percent: float
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SessionCreate(BaseModel):
    learning_path_id: UUID
    title: str


class SessionComplete(BaseModel):
    score: Optional[float] = None
    duration_minutes: Optional[float] = None


class SessionResponse(BaseModel):
    id: UUID
    user_id: UUID
    learning_path_id: UUID
    title: str
    content: Optional[str]
    duration_minutes: float
    score: Optional[float]
    session_number: int
    status: str
    started_at: datetime
    completed_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True
