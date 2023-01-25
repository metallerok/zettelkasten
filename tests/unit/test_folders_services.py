import pytest

from src.services.folders.creator import (
    FolderCreator,
    FolderCreationInput,
    FolderCreationError,
)
from src.services.folders.updater import (
    FolderUpdater,
    FolderUpdateError,
)
from src.services.folders.remover import (
    FolderRemover,
)

from src.repositories.folders import SAFoldersRepo
from src.models.primitives.folder import (
    FolderTitle,
    FolderColor,
)

from src.message_bus import events

from tests.helpers.users import make_test_user
from tests.helpers.folders import make_test_folder


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
        user_id=user.id,
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
        parent_id=folder.id,
    )

    child_folder = creator.create(
        data=child_folder_data,
        user_id=user.id,
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
        parent_id=wrong_parent_folder.id,
    )

    creator = FolderCreator(
        folders_repo=folders_repo,
    )

    with pytest.raises(FolderCreationError) as e:
        creator.create(
            data=data,
            user_id=user2.id,
        )

    assert e.value.message == f"Parent folder (uuid={str(wrong_parent_folder.id)}) not found"


def test_folder_update_service(db_session):
    user = make_test_user(db_session)
    folder = make_test_folder(db_session, user)
    parent_folder = make_test_folder(db_session, user)

    db_session.commit()

    folders_repo = SAFoldersRepo(db_session)

    updater = FolderUpdater(
        folders_repo=folders_repo,
    )

    data = {
        "title": FolderTitle("updated title"),
        "color": FolderColor("#121212"),
        "parent_id": parent_folder.id,
    }

    folder = updater.update(
        data=data,
        folder=folder,
        user_id=user.id,
    )

    assert folder
    assert folder.title == data["title"]
    assert folder.color == data["color"]
    assert folder.parent_id == data["parent_id"]

    emitted_events = updater.get_events()
    emitted_events_types = [type(e) for e in emitted_events]
    assert events.FolderUpdated in emitted_events_types


def test_try_update_folder_with_wrong_parent_by_user(db_session):
    user1 = make_test_user(db_session)
    user2 = make_test_user(db_session)

    folder = make_test_folder(db_session, user1)
    wrong_parent_folder = make_test_folder(db_session, user2)
    db_session.commit()

    folders_repo = SAFoldersRepo(db_session)

    data = {
        "parent_id": wrong_parent_folder.id,
    }

    updater = FolderUpdater(
        folders_repo=folders_repo,
    )

    with pytest.raises(FolderUpdateError) as e:
        updater.update(
            data=data,
            folder=folder,
            user_id=user1.id,
        )

    assert e.value.message == f"Parent folder (uuid={str(wrong_parent_folder.id)}) not found"


def test_folder_remove_service(db_session):
    user = make_test_user(db_session)
    folder = make_test_folder(db_session, user)

    db_session.commit()

    folders_repo = SAFoldersRepo(db_session)

    remover = FolderRemover(
        folders_repo=folders_repo,
    )

    remover.remove(
        folder=folder,
        user_id=user.id,
    )

    assert folder.deleted is not None

    db_session.commit()
    db_session.expire_all()

    assert folders_repo.get(id_=folder.id) is None

    emitted_events = remover.get_events()
    emitted_events_types = [type(e) for e in emitted_events]
    assert events.FolderRemoved in emitted_events_types
