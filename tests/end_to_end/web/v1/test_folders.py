from src.entrypoints.web.api.v1 import url
from falcon.status_codes import (
    HTTP_200,
    HTTP_401,
    HTTP_404,
)
from tests.helpers.headers import Headers
from tests.helpers.users import make_test_user
from tests.helpers.folders import make_test_folder
from tests.helpers.message_bus import DryRunMessageBus

from src.models.primitives.folder import (
    FolderTitle,
)

from src.repositories.folders import SAFoldersRepo

from src.message_bus import events

FOLDER_URL = url("/folder")
FOLDERS_URL = url("/folders")


def test_try_get_folder_without_auth(api):
    result = api.simulate_get(FOLDER_URL)

    assert result.status == HTTP_401


def test_get_folder(
        api,
        db_session,
        headers: Headers,
        auth_session_factory,
):
    user = make_test_user(db_session)
    folder = make_test_folder(db_session, user)

    another_user = make_test_user(db_session)
    another_user_folder = make_test_folder(db_session, another_user)

    auth_session = auth_session_factory(db_session, user)

    db_session.commit()

    headers.set_bearer_token(auth_session.access_token)

    req_params = {
        "folder_id": folder.id
    }

    result = api.simulate_get(
        FOLDER_URL, headers=headers.get(), params=req_params,
    )

    assert result.status == HTTP_200

    assert result.json["folder"]["id"] == str(folder.id)

    req_params = {
        "folder_id": str(another_user_folder.id)
    }

    result = api.simulate_get(
        FOLDER_URL, headers=headers.get(), params=req_params,
    )

    assert result.status == HTTP_404


def test_try_post_folder_without_auth(api):
    result = api.simulate_post(FOLDER_URL)

    assert result.status == HTTP_401


def test_post_folder(
        api_factory,
        db_session,
        headers: Headers,
        auth_session_factory,
):
    message_bus = DryRunMessageBus(
        event_handlers={
            events.FolderCreated: []
        }
    )

    api = api_factory(message_bus=message_bus)
    user = make_test_user(db_session)

    auth_session = auth_session_factory(db_session, user)

    db_session.commit()

    headers.set_bearer_token(auth_session.access_token)

    req_body = {
        "title": "folder title",
        "color": "#333fff",
    }

    result = api.simulate_post(
        FOLDER_URL, headers=headers.get(), json=req_body,
    )

    assert result.status == HTTP_200

    resp_folder = result.json["folder"]

    assert resp_folder["id"]
    assert resp_folder["title"] == req_body["title"]
    assert resp_folder["color"] == req_body["color"]
    assert resp_folder["parent_id"] is None
    assert "children_folders" in resp_folder

    emitted_messages = [type(m["message"]) for m in message_bus.messages]
    assert events.FolderCreated in emitted_messages


def test_try_patch_folder_without_auth(api):
    result = api.simulate_patch(FOLDER_URL)

    assert result.status == HTTP_401


def test_patch_folder(
        api_factory,
        db_session,
        headers: Headers,
        auth_session_factory,
):
    message_bus = DryRunMessageBus(
        event_handlers={
            events.FolderUpdated: []
        }
    )

    api = api_factory(message_bus=message_bus)
    user = make_test_user(db_session)
    folder = make_test_folder(db_session, user)

    auth_session = auth_session_factory(db_session, user)

    db_session.commit()

    headers.set_bearer_token(auth_session.access_token)

    req_params = {
        "folder_id": str(folder.id),
    }

    req_body = {
        "title": "updated folder title",
        "color": "#f3f3f3",
    }

    result = api.simulate_patch(
        FOLDER_URL, headers=headers.get(),
        json=req_body, params=req_params,
    )

    assert result.status == HTTP_200

    resp_folder = result.json["folder"]

    assert resp_folder["id"] == str(folder.id)
    assert resp_folder["title"] == req_body["title"]
    assert resp_folder["color"] == req_body["color"]

    emitted_messages = [type(m["message"]) for m in message_bus.messages]
    assert events.FolderUpdated in emitted_messages


def test_try_delete_folder_without_auth(api):
    result = api.simulate_delete(FOLDER_URL)

    assert result.status == HTTP_401


def test_delete_folder(
        api_factory,
        db_session,
        headers: Headers,
        auth_session_factory,
):
    message_bus = DryRunMessageBus(
        event_handlers={
            events.FolderRemoved: []
        }
    )

    api = api_factory(message_bus=message_bus)
    user = make_test_user(db_session)
    folder = make_test_folder(db_session, user)

    auth_session = auth_session_factory(db_session, user)

    db_session.commit()

    headers.set_bearer_token(auth_session.access_token)

    req_params = {
        "folder_id": str(folder.id)
    }

    result = api.simulate_delete(
        FOLDER_URL, headers=headers.get(),
        params=req_params,
    )

    assert result.status == HTTP_200

    emitted_messages = [type(m["message"]) for m in message_bus.messages]
    assert events.FolderRemoved in emitted_messages

    assert SAFoldersRepo(db_session).get(id_=folder.id) is None


def test_try_get_folders_without_auth(api):
    result = api.simulate_get(FOLDERS_URL)

    assert result.status == HTTP_401


def test_get_folders(
        api,
        db_session,
        headers: Headers,
        auth_session_factory,
):
    user = make_test_user(db_session)
    folder1 = make_test_folder(db_session, user)
    folder2 = make_test_folder(db_session, user)

    another_user = make_test_user(db_session)
    another_user_folder = make_test_folder(db_session, another_user)

    auth_session = auth_session_factory(db_session, user)

    db_session.commit()

    headers.set_bearer_token(auth_session.access_token)

    result = api.simulate_get(
        FOLDERS_URL, headers=headers.get()
    )

    assert result.status == HTTP_200
    assert len(result.json) == 2
    folders_ids = [f["folder"]["id"] for f in result.json]

    assert str(folder1.id) in folders_ids
    assert str(folder2.id) in folders_ids
    assert str(another_user_folder.id) not in folders_ids


def test_get_folders_by_parent_id(
        api,
        db_session,
        headers: Headers,
        auth_session_factory,
):
    user = make_test_user(db_session)
    parent_folder = make_test_folder(db_session, user)
    folder = make_test_folder(db_session, user)
    folder.parent = parent_folder

    auth_session = auth_session_factory(db_session, user)

    db_session.commit()

    headers.set_bearer_token(auth_session.access_token)

    req_params = {
        "parent_id": str(parent_folder.id)
    }

    result = api.simulate_get(
        FOLDERS_URL, headers=headers.get(), params=req_params,
    )

    assert result.status == HTTP_200
    assert len(result.json) == 1
    folders_ids = [f["folder"]["id"] for f in result.json]

    assert str(folder.id) in folders_ids


def test_get_folders_by_title(
        api,
        db_session,
        headers: Headers,
        auth_session_factory,
):
    user = make_test_user(db_session)
    folder1 = make_test_folder(db_session, user, title=FolderTitle("aaa"))
    folder2 = make_test_folder(db_session, user, title=FolderTitle("bbb"))

    auth_session = auth_session_factory(db_session, user)

    db_session.commit()

    headers.set_bearer_token(auth_session.access_token)

    req_params = {
        "title": "aaa",
    }

    result = api.simulate_get(
        FOLDERS_URL, headers=headers.get(), params=req_params,
    )

    assert result.status == HTTP_200
    assert len(result.json) == 1
    folders_ids = [f["folder"]["id"] for f in result.json]

    assert str(folder1.id) in folders_ids
    assert str(folder2.id) not in folders_ids
