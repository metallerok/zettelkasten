from sqlalchemy.orm import Session
from src.models.folder import Folder
from src.models.user import User
from src.models.primitives.folder import (
    FolderTitle,
    FolderColor,
)

from uuid import uuid4


def make_test_folder(db_session: Session, user: User) -> Folder:
    folder = Folder(
        id=str(uuid4()),
        title=FolderTitle("Test folder"),
        color=FolderColor("#ffffff"),
        user=user,
    )

    db_session.add(folder)

    return folder
