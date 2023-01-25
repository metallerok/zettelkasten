from sqlalchemy.orm import Session
from src.models.folder import Folder
from src.models.user import User
from src.models.primitives.folder import (
    FolderTitle,
    FolderColor,
)

from uuid import uuid4


def make_test_folder(db_session: Session, user: User, title: FolderTitle = None) -> Folder:
    folder = Folder(
        id=uuid4(),
        title=FolderTitle("Test folder") if title is None else title,
        color=FolderColor("#ffffff"),
        user=user,
    )

    db_session.add(folder)

    return folder
