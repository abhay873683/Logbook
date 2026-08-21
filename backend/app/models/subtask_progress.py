from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime

class SubtaskProgress(Base):
    __tablename__ = "subtask_progress"

    id = Column(Integer, primary_key=True, index=True)
    subtask_id = Column(Integer, ForeignKey("subtasks.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    progress = Column(Float, default=0.0)
    status = Column(String(30), default="In Progress")
    note = Column(String, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow)

    subtask = relationship("Subtask", back_populates="progress_list")
    user = relationship("User", back_populates="subtask_progress")