from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from typing import Optional, List, Dict, Union
from datetime import datetime

from models import MemoModel, EventModel, TaskModel
from models import Base  # 모델 정의 파일 경로를 맞춰야 함


class NoteRepository:
    """
    NoteRepository 클래스는 노트 데이터를 관리하는 역할을 수행합니다.
    """

    def __init__(self, db_url="sqlite:///notes.db"):
        """
        데이터베이스 연결 및 세션 초기화
        """
        self.engine = create_engine(db_url)
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()

        # 노트 타입에 따라 적절한 모델 선택
        self.model_mapping = {
            "memo": MemoModel,
            "event": EventModel,
            "task": TaskModel,
        }
        self.note_types = list(self.model_mapping.keys())

        # 테이블 생성
        Base.metadata.create_all(self.engine)

    def create(self, data: Dict) -> int:
        """
        새로운 노트를 생성하고 데이터베이스에 저장합니다.
        """

        NoteClass = self.model_mapping.get(data.get("type").lower())

        if not NoteClass:
            raise ValueError(f"Invalid note type: {data.get('type')}")

        if "date" in data:
            data["date"] = datetime.fromisoformat(data["date"])
        if "due_date" in data:
            data["due_date"] = datetime.fromisoformat(data["due_date"])

        note = NoteClass(**data)
        self.session.add(note)
        self.session.commit()
        return note.id

    def read(self, note_id: int, note_type: str) -> Optional[Dict]:
        """
        ID에 해당하는 노트를 반환합니다.
        """
        NoteClass = self.model_mapping.get(note_type.lower())

        note = self.session.query(NoteClass).filter_by(id=note_id).first()
        return note.to_dict() if note else None

    def read_all(self, note_type: str) -> List[Dict]:
        """
        모든 노트를 리스트 형태로 반환합니다.
        """
        NoteClass = self.model_mapping.get(note_type.lower())

        notes = self.session.query(NoteClass).all()
        return [note.to_dict() for note in notes]

    def update(self, note_id: int, updates: Dict) -> bool:
        """
        ID에 해당하는 노트를 업데이트합니다.
        """
        NoteClass = self.model_mapping.get(updates.get("type").lower())

        note = self.session.query(NoteClass).filter_by(id=note_id).first()
        if not note:
            return False

        note.from_dict(updates)

        self.session.commit()
        return True

    def delete(self, note_id: int, note_type: str) -> bool:
        """
        ID에 해당하는 노트를 삭제합니다.
        """
        NoteClass = self.model_mapping.get(note_type.lower())

        note = self.session.query(NoteClass).filter_by(id=note_id).first()
        if not note:
            return False

        self.session.delete(note)
        self.session.commit()
        return True
