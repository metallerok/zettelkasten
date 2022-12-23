from src.models.folder import Folder, FolderColor, FolderTitle
from tests.helpers.users import make_test_user

from uuid import uuid4


def test_folder_model(db_session):
    user = make_test_user(db_session)

    parent_folder = Folder(
        id=str(uuid4()),
        title=FolderTitle("Test parent folder"),
        color=FolderColor("#fff333"),
        user=user,
    )

    child_folder = Folder(
        id=str(uuid4()),
        title=FolderTitle("Test child folder"),
        color=FolderColor("#fff333"),
        parent_id=parent_folder.id,
        user=user,
    )

    db_session.add(parent_folder)
    db_session.add(child_folder)

    db_session.commit()
    db_session.expire_all()

    assert child_folder.parent == parent_folder
    assert len(parent_folder.children_folders) == 1
    assert parent_folder.children_folders[0] == child_folder
