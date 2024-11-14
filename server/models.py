from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Boolean, JSON
from typing import Dict, Any
from datetime import datetime

Base = declarative_base()


class BaseNoteModel(Base):
    __abstract__ = True  # 이 클래스는 테이블로 생성되지 않음

    id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(String, nullable=False)
    name = Column(String, nullable=False)
    tags = Column(JSON, default=[])  # 리스트 형태의 태그를 JSON으로 저장
    content = Column(String, nullable=False)
    created = Column(DateTime, default=datetime.utcnow)
    updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        """
        객체를 JSON 직렬화 가능한 딕셔너리로 변환
        """
        return {
            "id": self.id,
            "type": self.type,
            "name": self.name,
            "tags": self.tags,
            "content": self.content,
            "created": self.created.isoformat() if self.created else None,
            "updated": self.updated.isoformat() if self.updated else None,
        }

    def from_dict(self, data: Dict[str, Any]) -> "BaseNoteModel":
        """
        딕셔너리 데이터를 받아서 객체 생성
        """
        for key, value in data.items():
            if hasattr(self, key):
                if key in ["created", "updated"] and isinstance(value, str):
                    value = datetime.fromisoformat(value)  # 문자열을 datetime으로 변환
                setattr(self, key, value)


class MemoModel(BaseNoteModel):
    __tablename__ = "memos"

    # MemoModel만의 추가 필드 필요 시 여기에 추가 가능


class EventModel(BaseNoteModel):
    __tablename__ = "events"

    date = Column(DateTime, nullable=False)
    type = Column(String, nullable=False)

    def to_dict(self) -> Dict[str, Any]:
        """
        EventModel 고유의 필드 추가 변환
        """
        base_dict = super().to_dict()
        base_dict.update(
            {
                "date": self.date.isoformat() if self.date else None,
                "type": self.type,
            }
        )
        return base_dict

    def from_dict(self, data: Dict[str, Any]) -> "EventModel":
        """
        EventModel 고유 필드 변환 처리
        """
        super().from_dict(data)
        if "date" in data and isinstance(data["date"], str):
            self.date = datetime.fromisoformat(data["date"])


class TaskModel(BaseNoteModel):
    __tablename__ = "tasks"

    due_date = Column(DateTime, nullable=True)
    done = Column(Boolean, default=False)

    def to_dict(self) -> Dict[str, Any]:
        """
        TaskModel 고유의 필드 추가 변환
        """
        base_dict = super().to_dict()
        base_dict.update(
            {
                "due_date": self.due_date.isoformat() if self.due_date else None,
                "done": self.done,
            }
        )
        return base_dict

    def from_dict(self, data: Dict[str, Any]):
        """
        TaskModel 고유 필드 변환 처리
        """
        super().from_dict(data)
        if "due_date" in data and isinstance(data["due_date"], str):
            self.due_date = datetime.fromisoformat(data["due_date"])
