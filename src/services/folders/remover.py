import abc
from typing import List
from src.message_bus.types import Event
from src.message_bus import events
from src.models.folder import Folder
from src.repositories.folders import FoldersRepoABC

from uuid import UUID


class FolderRemoveError(Exception):
    def __init__(self, message: str = None):
        self.message = message

        super().__init__()


class FolderRemoverABC(abc.ABC):
    def __init__(self):
        self._events: List[Event] = []

    def get_events(self) -> List[Event]:
        return self._events

    @abc.abstractmethod
    def remove(
            self,
            folder: Folder,
            user_id: UUID,
    ):
        raise NotImplementedError


class FolderRemover(FolderRemoverABC):
    def __init__(
            self,
            folders_repo: FoldersRepoABC,
    ):
        self._folders_repo = folders_repo

        super().__init__()

    def remove(
            self,
            folder: Folder,
            user_id: UUID,
    ):
        self._folders_repo.remove(folder)

        self._events.append(
            events.FolderRemoved(
                id=str(folder.id),
                user_id=str(user_id),
            )
        )
