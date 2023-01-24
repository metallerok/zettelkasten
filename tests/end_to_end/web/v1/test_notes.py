import uuid

from src.entrypoints.web.api.v1 import url
from falcon.status_codes import (
    HTTP_200,
    HTTP_401,
    HTTP_404,
)
from tests.helpers.headers import Headers
from tests.helpers.users import make_test_user
from tests.helpers.folders import make_test_folder
from tests.helpers.notes import make_test_note
from tests.helpers.message_bus import DryRunMessageBus

from src.repositories.notes import SANotesRepo

from src.models.primitives.note import (
    NoteTitle,
)
from src.models.note import NoteToNoteRelation

from src.message_bus import events

from uuid import UUID


NOTE_URL = url("/note")
NOTES_URL = url("/notes")
NOTE_RELATION_URL = url("/note-relation")


def test_try_get_note_without_auth(api):
    result = api.simulate_get(NOTE_URL)

    assert result.status == HTTP_401


def test_get_note(
        api,
        db_session,
        headers: Headers,
        auth_session_factory,
):
    user = make_test_user(db_session)
    note = make_test_note(db_session, user)

    another_user = make_test_user(db_session)
    another_user_note = make_test_note(db_session, another_user)

    auth_session = auth_session_factory(db_session, user)

    db_session.commit()

    headers.set_bearer_token(auth_session.access_token)

    req_params = {
        "note_id": note.id
    }

    result = api.simulate_get(
        NOTE_URL, headers=headers.get(), params=req_params,
    )

    assert result.status == HTTP_200

    assert result.json["note"]["id"] == note.id

    req_params = {
        "note_id": another_user_note.id
    }

    result = api.simulate_get(
        NOTE_URL, headers=headers.get(), params=req_params,
    )

    assert result.status == HTTP_404


def test_try_post_note_without_auth(api):
    result = api.simulate_post(NOTE_URL)

    assert result.status == HTTP_401


def test_post_note(
        api_factory,
        db_session,
        headers: Headers,
        auth_session_factory,
):
    message_bus = DryRunMessageBus(
        event_handlers={
            events.NoteCreated: []
        }
    )

    api = api_factory(message_bus=message_bus)
    user = make_test_user(db_session)
    folder = make_test_folder(db_session, user)

    auth_session = auth_session_factory(db_session, user)

    db_session.commit()

    headers.set_bearer_token(auth_session.access_token)

    req_body = {
        "title": "folder title",
        "color": "#333fff",
        "text": "test",
        "folder_id": folder.id,
    }

    result = api.simulate_post(
        NOTE_URL, headers=headers.get(), json=req_body,
    )

    assert result.status == HTTP_200

    resp_note = result.json["note"]

    assert resp_note["id"]
    assert resp_note["title"] == req_body["title"]
    assert resp_note["color"] == req_body["color"]
    assert resp_note["text"] == req_body["text"]
    assert resp_note["folder_id"] == folder.id

    emitted_messages = [type(m["message"]) for m in message_bus.messages]
    assert events.NoteCreated in emitted_messages


def test_try_patch_note_without_auth(api):
    result = api.simulate_patch(NOTE_URL)

    assert result.status == HTTP_401


def test_patch_note(
        api_factory,
        db_session,
        headers: Headers,
        auth_session_factory,
):
    message_bus = DryRunMessageBus(
        event_handlers={
            events.NoteUpdated: []
        }
    )

    api = api_factory(message_bus=message_bus)
    user = make_test_user(db_session)
    note = make_test_note(db_session, user)
    folder = make_test_folder(db_session, user)

    auth_session = auth_session_factory(db_session, user)

    db_session.commit()

    headers.set_bearer_token(auth_session.access_token)

    req_params = {
        "note_id": note.id
    }

    req_body = {
        "title": "updated title",
        "color": "#f3f3f3",
        "text": "updated text",
        "folder_id": folder.id,
    }

    result = api.simulate_patch(
        NOTE_URL, headers=headers.get(),
        json=req_body, params=req_params,
    )

    assert result.status == HTTP_200

    resp_note = result.json["note"]

    assert resp_note["id"] == note.id
    assert resp_note["title"] == req_body["title"]
    assert resp_note["color"] == req_body["color"]
    assert resp_note["text"] == req_body["text"]
    assert resp_note["folder_id"] == folder.id

    emitted_messages = [type(m["message"]) for m in message_bus.messages]
    assert events.NoteUpdated in emitted_messages


def test_try_delete_note_without_auth(api):
    result = api.simulate_delete(NOTE_URL)

    assert result.status == HTTP_401


def test_delete_note(
        api_factory,
        db_session,
        headers: Headers,
        auth_session_factory,
):
    message_bus = DryRunMessageBus(
        event_handlers={
            events.NoteRemoved: []
        }
    )

    api = api_factory(message_bus=message_bus)
    user = make_test_user(db_session)
    note = make_test_note(db_session, user)

    auth_session = auth_session_factory(db_session, user)

    db_session.commit()

    headers.set_bearer_token(auth_session.access_token)

    req_params = {
        "note_id": note.id
    }

    result = api.simulate_delete(
        NOTE_URL, headers=headers.get(),
        params=req_params,
    )

    assert result.status == HTTP_200

    emitted_messages = [type(m["message"]) for m in message_bus.messages]
    assert events.NoteRemoved in emitted_messages

    assert SANotesRepo(db_session).get(id_=UUID(note.id)) is None


def test_try_get_notes_without_auth(api):
    result = api.simulate_get(NOTES_URL)

    assert result.status == HTTP_401


def test_get_notes(
        api,
        db_session,
        headers: Headers,
        auth_session_factory,
):
    user = make_test_user(db_session)
    note1 = make_test_note(db_session, user)
    note2 = make_test_note(db_session, user)

    another_user = make_test_user(db_session)
    another_user_note = make_test_note(db_session, another_user)

    auth_session = auth_session_factory(db_session, user)

    db_session.commit()

    headers.set_bearer_token(auth_session.access_token)

    result = api.simulate_get(
        NOTES_URL, headers=headers.get()
    )

    assert result.status == HTTP_200
    assert len(result.json) == 2
    notes_ids = [f["note"]["id"] for f in result.json]

    assert note1.id in notes_ids
    assert note2.id in notes_ids
    assert another_user_note.id not in notes_ids


def test_get_notes_by_title(
        api,
        db_session,
        headers: Headers,
        auth_session_factory,
):
    user = make_test_user(db_session)
    note1 = make_test_note(db_session, user, title=NoteTitle("aaa"))
    note2 = make_test_note(db_session, user, title=NoteTitle("bbb"))

    auth_session = auth_session_factory(db_session, user)

    db_session.commit()

    headers.set_bearer_token(auth_session.access_token)

    req_params = {
        "title": "aaa",
    }

    result = api.simulate_get(
        NOTES_URL, headers=headers.get(), params=req_params,
    )

    assert result.status == HTTP_200
    assert len(result.json) == 1
    notes_ids = [f["note"]["id"] for f in result.json]

    assert note1.id in notes_ids
    assert note2.id not in notes_ids


def test_try_create_note_relation_without_auth(api):
    result = api.simulate_patch(NOTE_RELATION_URL)

    assert result.status == HTTP_401


def test_create_note_relation(
        api_factory,
        db_session,
        headers: Headers,
        auth_session_factory,
):
    message_bus = DryRunMessageBus(
        event_handlers={
            events.NoteRelationCreated: []
        }
    )
    api = api_factory(message_bus=message_bus)

    user = make_test_user(db_session)
    parent_note = make_test_note(db_session, user)
    child_note = make_test_note(db_session, user)

    auth_session = auth_session_factory(db_session, user)

    db_session.commit()

    headers.set_bearer_token(auth_session.access_token)

    req_params = {
        "parent_note_id": parent_note.id,
        "child_note_id": child_note.id,
    }

    req_body = {
        "description": "desc",
    }

    result = api.simulate_patch(
        NOTE_RELATION_URL, headers=headers.get(),
        params=req_params, json=req_body,
    )

    assert result.status == HTTP_200
    assert len(result.json["note"]["notes_relations"]) == 1
    assert result.json["note"]["notes_relations"][0]["description"] == req_body["description"]

    emitted_messages = [type(m["message"]) for m in message_bus.messages]
    assert events.NoteRelationCreated in emitted_messages


def test_try_remove_note_relation_without_auth(api):
    result = api.simulate_delete(NOTE_RELATION_URL)

    assert result.status == HTTP_401


def test_remove_note_relation(
        api_factory,
        db_session,
        headers: Headers,
        auth_session_factory,
):
    message_bus = DryRunMessageBus(
        event_handlers={
            events.NoteRelationRemoved: []
        }
    )
    api = api_factory(message_bus=message_bus)

    user = make_test_user(db_session)
    parent_note = make_test_note(db_session, user)
    child_note = make_test_note(db_session, user)
    parent_note.notes_relations.append(
        NoteToNoteRelation(
            id=str(uuid.uuid4()),
            child_note=child_note,
        )
    )

    auth_session = auth_session_factory(db_session, user)

    db_session.commit()

    headers.set_bearer_token(auth_session.access_token)

    req_params = {
        "parent_note_id": parent_note.id,
        "child_note_id": child_note.id,
    }

    assert len(parent_note.notes_relations) == 1

    result = api.simulate_delete(
        NOTE_RELATION_URL, headers=headers.get(),
        params=req_params
    )

    assert result.status == HTTP_200
    assert len(result.json["note"]["notes_relations"]) == 0

    emitted_messages = [type(m["message"]) for m in message_bus.messages]
    assert events.NoteRelationRemoved in emitted_messages
