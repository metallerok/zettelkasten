import pytest

from src.services.folders.creator import (
    FolderCreator,
    FolderCreationInput,
    FolderCreationError,
)

from src.repositories.folders import SAFoldersRepo
from src.models.primitives.folder import (
    FolderTitle,
    FolderColor,
)

from src.message_bus import events

from tests.helpers.users import make_test_user
from tests.helpers.folders import make_test_folder

from uuid import UUID


def test_folder_creation_service(db_session):
    user = make_test_user(db_session)

    folders_repo = SAFoldersRepo(db_session)

    data = FolderCreationInput(
        title=FolderTitle("Test folder"),
        color=FolderColor("#333ccc"),
    )

    creator = FolderCreator(
        folders_repo=folders_repo,
    )

    folder = creator.create(
        data=data,
        user_id=UUID(user.id),
    )

    assert folder
    assert folder.title == data.title
    assert folder.color == data.color
    assert folder.parent_id is None

    emitted_events = creator.get_events()
    emitted_events_types = [type(e) for e in emitted_events]
    assert events.FolderCreated in emitted_events_types

    child_folder_data = FolderCreationInput(
        title=FolderTitle("Test Child folder"),
        parent_id=UUID(folder.id),
    )

    child_folder = creator.create(
        data=child_folder_data,
        user_id=UUID(user.id),
    )

    assert child_folder
    assert child_folder.title == child_folder_data.title
    assert child_folder.color is None
    assert child_folder.parent_id == folder.id
    assert child_folder.parent == folder


def test_try_create_folder_with_wrong_parent_by_user(db_session):
    user1 = make_test_user(db_session)
    user2 = make_test_user(db_session)

    wrong_parent_folder = make_test_folder(db_session, user1)
    db_session.commit()

    folders_repo = SAFoldersRepo(db_session)

    data = FolderCreationInput(
        title=FolderTitle("Test folder"),
        color=FolderColor("#333ccc"),
        parent_id=UUID(wrong_parent_folder.id)
    )

    creator = FolderCreator(
        folders_repo=folders_repo,
    )

    with pytest.raises(FolderCreationError) as e:
        creator.create(
            data=data,
            user_id=UUID(user2.id),
        )

    assert e.value.message == f"Parent folder (uuid={str(wrong_parent_folder.id)}) not found"
