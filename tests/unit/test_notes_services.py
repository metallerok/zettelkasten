import uuid

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

from src.services.notes.relation_creator import (
    NoteRelationCreationError,
    NoteRelationCreator,
    NoteRelationCreationInput,
)

from src.services.notes.relation_remover import (
    NoteRelationRemover,
)

from src.repositories.notes import SANotesRepo
from src.repositories.folders import SAFoldersRepo
from src.models.primitives.note import (
    NoteTitle,
    NoteColor,
)
from src.models.note import NoteToNoteRelation

from src.message_bus import events

from tests.helpers.users import make_test_user
from tests.helpers.folders import make_test_folder
from tests.helpers.notes import make_test_note


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
        user_id=user.id,
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
        "folder_id": folder.id,
    }

    note = updater.update(
        data=data,
        note=note,
        user_id=user.id,
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
        "folder_id": wrong_folder.id
    }

    with pytest.raises(NoteUpdateError) as e:
        updater.update(
            data=data,
            note=note,
            user_id=user1.id,
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
        user_id=user.id,
    )

    assert note.deleted is not None

    db_session.commit()
    db_session.expire_all()

    assert notes_repo.get(id_=note.id) is None

    emitted_events = remover.get_events()
    emitted_events_types = [type(e) for e in emitted_events]
    assert events.NoteRemoved in emitted_events_types


def test_try_create_note_relation_but_wrong_user(db_session):
    user1 = make_test_user(db_session)
    note1 = make_test_note(db_session, user1)

    user2 = make_test_user(db_session)
    note2 = make_test_note(db_session, user2)

    db_session.commit()

    relation_creator = NoteRelationCreator()

    with pytest.raises(NoteRelationCreationError):
        relation_creator.create(
            data=NoteRelationCreationInput(
                parent_note=note1,
                child_note=note2,
            ),
            user_id=user1.id,
        )


def test_create_note_relation(db_session):
    user = make_test_user(db_session)
    parent_note = make_test_note(db_session, user)
    child_note = make_test_note(db_session, user)

    db_session.commit()

    relation_creator = NoteRelationCreator()

    data = NoteRelationCreationInput(
        parent_note=parent_note,
        child_note=child_note,
        description="description",
    )

    parent_note = relation_creator.create(
        data=data,
        user_id=user.id,
    )

    db_session.commit()
    db_session.expire_all()

    children_notes = {nr.child_note_id: nr for nr in parent_note.notes_relations}

    assert child_note.id in children_notes
    assert children_notes[child_note.id].description == data.description

    emitted_events = relation_creator.get_events()
    emitted_events_types = [type(e) for e in emitted_events]
    assert events.NoteRelationCreated in emitted_events_types


def test_try_create_note_relation_but_already_exists(db_session):
    user = make_test_user(db_session)
    parent_note = make_test_note(db_session, user)
    child_note = make_test_note(db_session, user)

    parent_note.notes_relations.append(
        NoteToNoteRelation(
            id=uuid.uuid4(),
            child_note=child_note,
            description="desc",
        )
    )

    db_session.commit()

    assert len(parent_note.notes_relations) == 1

    relation_creator = NoteRelationCreator()

    data = NoteRelationCreationInput(
        parent_note=parent_note,
        child_note=child_note,
        description="update description",
    )

    parent_note = relation_creator.create(
        data=data,
        user_id=user.id,
    )

    db_session.commit()
    db_session.expire_all()

    children_notes = {nr.child_note_id: nr for nr in parent_note.notes_relations}

    assert child_note.id in children_notes
    assert children_notes[child_note.id].description == data.description

    emitted_events = relation_creator.get_events()
    emitted_events_types = [type(e) for e in emitted_events]
    assert events.NoteRelationCreated not in emitted_events_types


def test_remove_note_relation(db_session):
    user = make_test_user(db_session)
    parent_note = make_test_note(db_session, user)
    child_note = make_test_note(db_session, user)

    parent_note.notes_relations.append(
        NoteToNoteRelation(
            id=uuid.uuid4(),
            child_note=child_note,
        )
    )

    db_session.commit()

    relation_remover = NoteRelationRemover()

    parent_note = relation_remover.remove(
        parent_note=parent_note,
        child_note=child_note,
        user_id=user.id,
    )

    db_session.commit()
    db_session.expire_all()

    children_notes = {nr.child_note_id: nr for nr in parent_note.notes_relations}

    assert child_note.id not in children_notes

    emitted_events = relation_remover.get_events()
    emitted_events_types = [type(e) for e in emitted_events]
    assert events.NoteRelationRemoved in emitted_events_types
