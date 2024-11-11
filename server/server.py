from server.note import Note, Memo, Event, Task
from server.database import NoteRepository


class JarvisServer:
    database: list = []
    repository: NoteRepository = NoteRepository()

    @classmethod
    def create_memo(cls, name: str, content: str):
        memo = Memo(name, content)
        cls.database.append(memo)

    @classmethod
    def count_memo(cls) -> int:
        return len(cls.database)

    @classmethod
    def latest_memo(cls) -> Memo:
        return cls.database.pop()
