import pytest
from src.services.notes.creator import (
    NoteCreationInput,
    NoteCreator,
)

from src.services.notes.updater import (
    NoteUpdater,
    NoteUpdateError,
)

from src.services.notes.remover import (
    NoteRemover,
)

from src.repositories.notes import SANotesRepo
from src.repositories.folders import SAFoldersRepo
from src.models.primitives.note import (
    NoteTitle,
    NoteColor,
)

from src.message_bus import events

from tests.helpers.users import make_test_user
from tests.helpers.folders import make_test_folder
from tests.helpers.notes import make_test_note

from uuid import UUID


def test_note_creation_service(db_session):
    user = make_test_user(db_session)
    folder = make_test_folder(db_session, user)

    notes_repo = SANotesRepo(db_session)

    data = NoteCreationInput(
        title=NoteTitle("Test note"),
        color=NoteColor("#333ccc"),
        text="test",
    )

    creator = NoteCreator(
        notes_repo=notes_repo,
    )

    note = creator.create(
        data=data,
        folder=folder,
        user_id=UUID(user.id),
    )

    db_session.commit()

    assert note
    assert note.title == data.title
    assert note.color == data.color
    assert note.folder == folder
    assert note.text == data.text

    emitted_events = creator.get_events()
    emitted_events_types = [type(e) for e in emitted_events]
    assert events.NoteCreated in emitted_events_types


def test_note_update_service(db_session):
    user = make_test_user(db_session)
    note = make_test_note(db_session, user)
    folder = make_test_folder(db_session, user)

    db_session.commit()

    folders_repo = SAFoldersRepo(db_session)

    updater = NoteUpdater(
        folders_repo=folders_repo,
    )

    data = {
        "title": NoteTitle("updated title"),
        "color": NoteColor("#121212"),
        "text": "updated text",
        "folder_id": UUID(folder.id),
    }

    note = updater.update(
        data=data,
        note=note,
        user_id=UUID(user.id),
    )

    assert note
    assert note.title == data["title"]
    assert note.color == data["color"]
    assert note.text == data["text"]
    assert note.folder_id == folder.id

    emitted_events = updater.get_events()
    emitted_events_types = [type(e) for e in emitted_events]
    assert events.NoteUpdated in emitted_events_types


def test_try_update_note_with_wrong_folder(db_session):
    user1 = make_test_user(db_session)
    user2 = make_test_user(db_session)

    note = make_test_note(db_session, user1)

    wrong_folder = make_test_folder(db_session, user2)

    db_session.commit()

    folders_repo = SAFoldersRepo(db_session)

    updater = NoteUpdater(
        folders_repo=folders_repo,
    )

    data = {
        "folder_id": UUID(wrong_folder.id)
    }

    with pytest.raises(NoteUpdateError) as e:
        updater.update(
            data=data,
            note=note,
            user_id=UUID(user1.id),
        )

    assert e.value.message == f"Note update error. Folder (uuid={str(wrong_folder.id)}) not found"


def test_note_remove_service(db_session):
    user = make_test_user(db_session)
    note = make_test_note(db_session, user)

    db_session.commit()

    notes_repo = SANotesRepo(db_session)

    remover = NoteRemover(
        notes_repo=notes_repo,
    )

    remover.remove(
        note=note,
        user_id=UUID(user.id),
    )

    assert note.deleted is not None

    db_session.commit()
    db_session.expire_all()

    assert notes_repo.get(id_=UUID(note.id)) is None

    emitted_events = remover.get_events()
    emitted_events_types = [type(e) for e in emitted_events]
    assert events.NoteRemoved in emitted_events_types
