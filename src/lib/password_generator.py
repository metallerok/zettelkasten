import abc
import secrets
import string


class PasswordGeneratorABC(abc.ABC):
    @abc.abstractmethod
    def generate(self, length: int = 8) -> str:
        raise NotImplementedError


class PasswordGenerator(PasswordGeneratorABC):
    def generate(self, length: int = 8) -> str:
        alphabet = string.ascii_letters + string.digits
        password = ''.join(secrets.choice(alphabet) for i in range(length))

        return password
