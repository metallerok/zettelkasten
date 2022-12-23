from .base import HTTPBadRequest, HTTPNotFound


class HTTPWrongUserData(HTTPBadRequest):
    code = 1001001

    def __init__(self, message: str = None):
        default_message = "Wrong user data"

        if message:
            default_message = f'{default_message}. {message}'

        super().__init__(
            description={
                "code": self.code,
                "message": default_message,
            }
        )


class HTTPPasswordChangingError(HTTPBadRequest):
    code = 1001002

    def __init__(self):
        super().__init__(
            description={
                "code": self.code,
                "message": "Password changing error",
            }
        )


class HTTPUserNotFound(HTTPNotFound):
    code = 2001001

    def __init__(self, id_: str = None):
        if id_:
            message = f"User (id={id}) not found"
        else:
            message = "User not found"

        super().__init__(
            description={
                "code": self.code,
                "message": message,
            }
        )
