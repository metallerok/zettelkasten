import abc
from typing import List
from dataclasses import dataclass

from src.repositories.users import UsersRepoABC

from src.models.user import User
from src.models.primitives.user import (
    FirstName,
    LastName,
    MiddleName,
    Email,
)

from src.message_bus.types import Message
from src.message_bus import events

from uuid import uuid4


class RegistrationError(Exception):
    pass


class UserCreationError(RegistrationError):
    def __init__(self, message: str = None):
        self.message = message

        super().__init__()


@dataclass
class RegistrationInput:
    last_name: LastName
    first_name: FirstName
    middle_name: MiddleName
    email: Email
    password: str = None


class RegistrationServiceABC(abc.ABC):
    def register(self, data: RegistrationInput) -> User:
        raise NotImplementedError


class RegistrationService(RegistrationServiceABC):
    def __init__(
            self,
            users_repo: UsersRepoABC,
    ):
        self._users_repo = users_repo
        self._events: List[Message] = []

    def register(self, data: RegistrationInput) -> User:
        self._check_user_doesnt_exists(data)

        user = User(
            id=uuid4(),
            email=data.email,
            first_name=data.first_name,
            last_name=data.last_name,
            middle_name=data.middle_name,
            password=User.make_password_hash(data.password),
        )

        self._users_repo.add(user)

        self._events.append(
            events.UserCreated(
                id=user.id,
            )
        )

        return user

    def _check_user_doesnt_exists(self, data: RegistrationInput):
        user = self._users_repo.get_by_email(data.email, with_deleted=True)

        if user:
            raise UserCreationError

    def get_events(self) -> List[Message]:
        return self._events
