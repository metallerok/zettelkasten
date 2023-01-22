from src.services.notes.creator import (
    NoteCreationInput,
    NoteCreator,
)

from src.repositories.notes import SANotesRepo
from src.models.primitives.note import (
    NoteTitle,
    NoteColor,
)

from src.message_bus import events

from tests.helpers.users import make_test_user
from tests.helpers.folders import make_test_folder

from uuid import UUID


def test_note_creation_service(db_session):
    user = make_test_user(db_session)
    folder = make_test_folder(db_session, user)

    notes_repo = SANotesRepo(db_session)

    data = NoteCreationInput(
        title=NoteTitle("Test note"),
        color=NoteColor("#333ccc"),
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

    emitted_events = creator.get_events()
    emitted_events_types = [type(e) for e in emitted_events]
    assert events.NoteCreated in emitted_events_types
