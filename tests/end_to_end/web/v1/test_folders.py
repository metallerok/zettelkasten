from src.entrypoints.web.api.v1 import url
from falcon.status_codes import (
    HTTP_200,
    HTTP_401,
)
from tests.helpers.headers import Headers
from tests.helpers.users import make_test_user
from tests.helpers.message_bus import DryRunMessageBus
from src.message_bus import events

FOLDER_URL = url("/folder")


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
