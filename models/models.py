from sqlalchemy import Column, Boolean, String, UUID, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base
from uuid import uuid4
from datetime import datetime, timezone


Base = declarative_base()

class User(Base):
    __tablename__ = "user_details"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    first_name = Column(String)
    middle_name = Column(String, default=None)
    last_name = Column(String)
    full_name = Column(String)
    email = Column(String, unique=True)
    phone_number = Column(String, unique=True)
    password = Column(String)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

class todo_tasks(Base):
    __tablename__ = "todo_tasks"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(ForeignKey("user_details.id"), nullable=False)
    task_description = Column(String)
    is_completed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

