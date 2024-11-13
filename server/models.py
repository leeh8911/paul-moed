from sqlalchemy import create_engine, Column, String, Integer, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class NoteModel(Base):
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    content = Column(String, nullable=False)
    created = Column(DateTime, default=datetime.utcnow)
    updated = Column(DateTime, default=datetime.utcnow)
    type = Column(String)  # Column to distinguish between note types

    __mapper_args__ = {"polymorphic_on": type, "polymorphic_identity": "note"}


# Memo model
class MemoModel(NoteModel):
    """
    Memo model class inheriting from NoteModel.
    """

    __mapper_args__ = {"polymorphic_identity": "memo"}


# Event model
class EventModel(NoteModel):
    """
    Event model class inheriting from NoteModel.
    """

    __mapper_args__ = {"polymorphic_identity": "event"}
    date = Column(DateTime, nullable=False)


# Task model
class TaskModel(NoteModel):
    """
    Task model class inheriting from NoteModel.
    """

    __mapper_args__ = {"polymorphic_identity": "task"}
    due_date = Column(DateTime, nullable=True)
    done = Column(Boolean, default=False)
