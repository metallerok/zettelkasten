import abc
from typing import List
from dataclasses import dataclass
from src.message_bus.types import Event
from src.message_bus import events
from src.models.folder import Folder
from src.models.primitives.folder import (
    FolderColor,
    FolderTitle,
)
from src.repositories.folders import FoldersRepoABC

from uuid import uuid4, UUID


@dataclass()
class FolderCreationInput:
    title: FolderTitle
    color: FolderColor = None
    parent_id: UUID = None


class FolderCreationError(Exception):
    def __init__(self, message: str = None):
        self.message = message

        super().__init__()


class FolderCreatorABC(abc.ABC):
    def __init__(self):
        self._events: List[Event] = []

    def get_events(self) -> List[Event]:
        return self._events

    @abc.abstractmethod
    def create(
            self,
            data: FolderCreationInput,
            user_id: UUID,
    ) -> Folder:
        raise NotImplementedError


class FolderCreator(FolderCreatorABC):
    def __init__(
            self,
            folders_repo: FoldersRepoABC,
    ):
        self._folders_repo = folders_repo

        super().__init__()

    def create(
            self,
            data: FolderCreationInput,
            user_id: UUID,
    ) -> Folder:
        parent = None
        if data.parent_id:
            parent = self._folders_repo.get(id_=data.parent_id, user_id=user_id)

            if parent is None:
                raise FolderCreationError(
                    message=f"Parent folder (uuid={str(data.parent_id)}) not found"
                )

        folder = Folder(
            id=str(uuid4()),
            title=data.title,
            color=data.color,
            parent_id=str(data.parent_id) if data.parent_id else None,
            parent=parent,
            user_id=str(user_id),
        )

        self._folders_repo.add(folder)

        self._events.append(
            events.FolderCreated(
                id=str(folder.id),
                user_id=str(user_id),
            )
        )

        return folder
