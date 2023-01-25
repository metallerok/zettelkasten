import abc
from typing import List
from copy import deepcopy
from src.message_bus.types import Event
from src.message_bus import events
from src.models.note import Note

from src.repositories.folders import FoldersRepoABC

from uuid import UUID


class NoteUpdateError(Exception):
    def __init__(self, message: str = None):
        self.message = message

        super().__init__()


class NoteUpdaterABC(abc.ABC):
    def __init__(self):
        self._events: List[Event] = []

    def get_events(self) -> List[Event]:
        return self._events

    @abc.abstractmethod
    def update(
            self,
            data: dict,
            note: Note,
            user_id: UUID,
    ) -> Note:
        raise NotImplementedError


class NoteUpdater(NoteUpdaterABC):
    def __init__(
            self,
            folders_repo: FoldersRepoABC
    ):
        self._folders_repo = folders_repo

        super().__init__()

    def update(
            self,
            data: dict,
            note: Note,
            user_id: UUID,
    ) -> Note:
        data = deepcopy(data)
        updated_fields = {}
        folder = None

        folder_id = data.pop("folder_id", None)
        if folder_id:
            folder = self._folders_repo.get(id_=folder_id, user_id=user_id)

            if folder is None:
                raise NoteUpdateError(
                    message=f"Note update error. Folder (uuid={str(folder_id)}) not found"
                )

        if folder:
            note.folder_id = folder.id
            updated_fields["folder_id"] = folder.id

        for key, value in data.items():
            if hasattr(note, key):
                updated_fields[key] = value
                setattr(note, key, value)

        self._events.append(
            events.NoteUpdated(
                id=folder.id,
                updated_fields=updated_fields,
                user_id=user_id,
            )
        )

        return note
