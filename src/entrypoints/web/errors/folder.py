from .base import HTTPBadRequest, HTTPNotFound


class HTTPFolderNotFound(HTTPNotFound):
    code = 2002001

    def __init__(self, id_: str = None):
        if id_:
            message = f"Folder (id={id}) not found"
        else:
            message = "Folder not found"

        super().__init__(
            description={
                "code": self.code,
                "message": message,
            }
        )


class HTTPFolderCreationError(HTTPBadRequest):
    code = 1002001

    def __init__(self, message: str = None):
        default_message = "Folder creation error"

        if message:
            default_message = f'{default_message}. {message}'

        super().__init__(
            description={
                "code": self.code,
                "message": default_message,
            }
        )
