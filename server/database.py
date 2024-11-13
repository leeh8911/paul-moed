from models import NoteModel, MemoModel, EventModel, TaskModel
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from typing import Optional, List, Dict, Union


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

    def create(
        self, note_type: str, name: str, content: str, metadata: Optional[Dict] = None
    ) -> int:
        """
        새로운 노트를 생성하고 데이터베이스에 저장합니다.
        """
        # 노트 타입에 따라 적절한 모델 선택
        model_mapping = {
            "memo": MemoModel,
            "event": EventModel,
            "task": TaskModel,
        }

        NoteClass = model_mapping.get(note_type.lower())
        if not NoteClass:
            raise ValueError(f"Invalid note type: {note_type}")

        note = NoteClass(name=name, content=content, **(metadata or {}))
        self.session.add(note)
        self.session.commit()
        return note.id

    def read(self, note_id: int) -> Optional[Dict]:
        """
        ID에 해당하는 노트를 반환합니다.
        """
        note = self.session.query(NoteModel).filter_by(id=note_id).first()
        return note.to_dict() if note else None

    def read_all(self) -> List[Dict]:
        """
        모든 노트를 리스트 형태로 반환합니다.
        """
        notes = self.session.query(NoteModel).all()
        return [note.to_dict() for note in notes]

    def update(self, note_id: int, updates: Dict) -> bool:
        """
        ID에 해당하는 노트를 업데이트합니다.
        """
        note = self.session.query(NoteModel).filter_by(id=note_id).first()
        if not note:
            return False

        for key, value in updates.items():
            setattr(note, key, value)

        self.session.commit()
        return True

    def delete(self, note_id: int) -> bool:
        """
        ID에 해당하는 노트를 삭제합니다.
        """
        note = self.session.query(NoteModel).filter_by(id=note_id).first()
        if not note:
            return False

        self.session.delete(note)
        self.session.commit()
        return True
