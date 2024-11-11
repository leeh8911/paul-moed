from datetime import datetime


class Note:
    """
    Abstract base class for different types of notes.
    """

    def __init__(self, name: str, content: str, created: datetime):
        """
        Initialize a note with a name and content.

        Args:
            name (str): The name of the note.
            content (str): The content of the note.
        """
        self._name = name
        self._content = content
        self._created = created
        self._updated = created

    @property
    def name(self) -> str:
        """Gets the name of the note."""
        return self._name

    @name.setter
    def name(self, name: str):
        """Sets the name of the note."""
        self._name = name
        self._updated = datetime.now()

    @property
    def content(self) -> str:
        """Gets the content of the note."""
        return self._content

    @content.setter
    def content(self, content: str):
        """Sets the content of the note."""
        self._content = content
        self._updated = datetime.now()

    @property
    def created(self) -> datetime:
        return self._created

    @property
    def updated(self) -> datetime:
        return self._updated


class Memo(Note):
    """
    A class representing a simple memo, inheriting from Note.
    """

    def __init__(self, name: str, content: str):
        """
        Initialize a Memo instance with a name and content.

        Args:
            name (str): The name of the memo.
            content (str): The content of the memo.
        """
        super().__init__(name, content, datetime.now())


class Event(Note):
    """
    A class representing an event, inheriting from Note.
    Adds a date attribute to represent the event date.
    """

    def __init__(self, name: str, content: str, date: datetime):
        """
        Initialize an Event instance with a name, content, and date.

        Args:
            name (str): The name of the event.
            content (str): The description of the event.
            date (str): The date of the event.
        """
        super().__init__(name, content, datetime.now())
        self._date = date  # Date of the event


class Task(Note):
    """
    A class representing a task, inheriting from Note.
    Adds a due_date attribute to represent the task deadline.
    """

    def __init__(self, name: str, content: str, due_date: datetime):
        """
        Initialize a Task instance with a name, content, and due date.

        Args:
            name (str): The name of the task.
            content (str): The details of the task.
            due_date (str): The due date for the task.
        """
        super().__init__(name, content, datetime.now())
        self._due_date = due_date  # Due date of the task
        self._done = False

    def mark_done(self):
        """Marks the task as complete."""
        self._done = True
        self._updated = datetime.now()
