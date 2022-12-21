import bcrypt
import hashlib
from typing import Optional
from abc import ABC, abstractmethod


class EncoderABC(ABC):
    def __init__(self, salt: Optional[str] = None):
        self.salt = salt

    @abstractmethod
    def encode(self, value: str) -> str:
        pass

    @abstractmethod
    def validate(self, verifiable: str, current_hash: str) -> bool:
        pass


class PasswordEncoder(EncoderABC):
    def encode(self, value: str) -> str:
        hash_ = bcrypt.hashpw(password=value.encode('utf-8'), salt=bcrypt.gensalt())
        return hash_.decode('utf-8')

    def validate(self, verifiable: str, current_hash: str) -> bool:
        return bcrypt.checkpw(verifiable.encode('utf-8'), current_hash.encode('utf-8'))


class TokenEncoder(EncoderABC):

    def encode(self, value: str) -> str:
        template = 'token.{%s}.salt.{%s}'
        token_ = template % (value, self.salt)

        return hashlib.sha256(token_.encode('utf-8')).hexdigest()

    def validate(self, verifiable: str, current_hash: str) -> bool:
        return self.encode(verifiable) == current_hash
