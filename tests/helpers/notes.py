from sqlalchemy.orm import Session
from src.models.folder import Folder
from src.models.note import Note
from src.models.user import User
from src.models.primitives.note import (
    NoteTitle,
    NoteColor,
)

from uuid import uuid4


def make_test_note(
        db_session: Session,
        user: User,
        folder: Folder = None,
        title: NoteTitle = None,
) -> Note:
    note = Note(
        id=uuid4(),
        title=NoteTitle("Test note") if title is None else title,
        color=NoteColor("#ffffff"),
        folder=folder,
        user=user,
    )

    db_session.add(note)

    return note
