from time import time
import jwt


class JWTToken:
    def __init__(self, token: str, secret: str):
        self.payload = {}
        self.secret = secret

        try:
            self.payload = jwt.decode(token, key=secret)
        except jwt.PyJWTError:
            pass

    def is_valid(self) -> bool:
        if not self.payload:
            return False

        expires_in = self.payload.get('exp')
        if expires_in is not None:
            return not expires_in < time()

        return True

    def __getitem__(self, item):
        return self.payload.get(item)

    def __contains__(self, item):
        return item in self.payload

    def __str__(self):
        return self.token

    @property
    def token(self) -> str:
        return jwt.encode(self.payload, key=self.secret).decode('utf-8')

    @staticmethod
    def create(payload: dict, secret: str) -> str:
        return jwt.encode(payload, secret).decode('utf-8')
