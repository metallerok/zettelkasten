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
from src.message_bus import events

FOLDER_URL = url("/folder")


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

    assert result.json["id"] == folder.id

    req_params = {
        "folder_id": another_user_folder.id
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

    assert result.json["id"]
    assert result.json["title"] == req_body["title"]
    assert result.json["color"] == req_body["color"]
    assert result.json["parent_id"] is None
    assert "children_folders" in result.json

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
        "folder_id": folder.id
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

    assert result.json["id"] == folder.id
    assert result.json["title"] == req_body["title"]
    assert result.json["color"] == req_body["color"]

    emitted_messages = [type(m["message"]) for m in message_bus.messages]
    assert events.FolderUpdated in emitted_messages
