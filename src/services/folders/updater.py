import abc
from typing import List
from copy import deepcopy
from src.message_bus.types import Event
from src.message_bus import events
from src.models.folder import Folder
from src.repositories.folders import FoldersRepoABC

from uuid import UUID


class FolderUpdateError(Exception):
    def __init__(self, message: str = None):
        self.message = message

        super().__init__()


class FolderUpdaterABC(abc.ABC):
    def __init__(self):
        self._events: List[Event] = []

    def get_events(self) -> List[Event]:
        return self._events

    @abc.abstractmethod
    def update(
            self,
            data: dict,
            folder: Folder,
            user_id: UUID,
    ) -> Folder:
        raise NotImplementedError


class FolderUpdater(FolderUpdaterABC):
    def __init__(
            self,
            folders_repo: FoldersRepoABC,
    ):
        self._folders_repo = folders_repo

        super().__init__()

    def update(
            self,
            data: dict,
            folder: Folder,
            user_id: UUID,
    ) -> Folder:
        data = deepcopy(data)
        updated_fields = {}
        parent = None

        parent_id = data.pop("parent_id", None)
        if parent_id:
            parent = self._folders_repo.get(id_=parent_id, user_id=user_id)

            if parent is None:
                raise FolderUpdateError(
                    message=f"Parent folder (uuid={str(parent_id)}) not found"
                )

        if parent:
            folder.parent_id = parent.id
            updated_fields["parent_id"] = parent.id

        for key, value in data.items():
            if hasattr(folder, key):
                updated_fields[key] = value
                setattr(folder, key, value)

        self._events.append(
            events.FolderUpdated(
                id=folder.id,
                updated_fields=updated_fields,
                user_id=user_id,
            )
        )

        return folder
