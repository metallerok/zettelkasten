import datetime as dt
from src.models.folder import Folder, FolderTitle
from src.models.note import Note, NoteTitle
from src.models.tag import Tag, TagTitle
from tests.helpers.users import make_test_user

from uuid import uuid4


def test_folder_tag(db_session):
    user = make_test_user(db_session)

    folder = Folder(
        id=uuid4(),
        title=FolderTitle("test folder"),
        user=user,
    )

    tag = Tag(
        id=uuid4(),
        title=TagTitle("test_tag"),
        user=user,
    )

    db_session.add(folder)
    db_session.add(tag)

    folder.tags.append(tag)

    db_session.commit()
    db_session.expire_all()

    assert len(folder.tags) == 1
    assert folder.tags[0] == tag

    tag.deleted = dt.datetime.utcnow()

    db_session.commit()
    db_session.expire_all()

    assert len(folder.tags) == 0


def test_note_tag(db_session):
    user = make_test_user(db_session)

    note = Note(
        id=uuid4(),
        title=NoteTitle("test note"),
        user=user,
    )

    tag = Tag(
        id=uuid4(),
        title=TagTitle("test_tag"),
        user=user,
    )

    db_session.add(note)
    db_session.add(tag)

    note.tags.append(tag)

    db_session.commit()
    db_session.expire_all()

    assert len(note.tags) == 1
    assert note.tags[0] == tag

    tag.deleted = dt.datetime.utcnow()

    db_session.commit()
    db_session.expire_all()

    assert len(note.tags) == 0
