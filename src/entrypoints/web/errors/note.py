from .base import HTTPBadRequest, HTTPNotFound


class HTTPNoteNotFound(HTTPNotFound):
    code = 2003001

    def __init__(self, id_: str = None):
        if id_:
            message = f"Note (id={id}) not found"
        else:
            message = "Note not found"

        super().__init__(
            description={
                "code": self.code,
                "message": message,
            }
        )


class HTTPNoteCreationError(HTTPBadRequest):
    code = 1003001

    def __init__(self, message: str = None):
        default_message = "Note creation error"

        if message:
            default_message = f'{default_message}. {message}'

        super().__init__(
            description={
                "code": self.code,
                "message": default_message,
            }
        )


class HTTPNoteUpdateError(HTTPBadRequest):
    code = 1003002

    def __init__(self, message: str = None):
        default_message = "Note update error"

        if message:
            default_message = f'{default_message}. {message}'

        super().__init__(
            description={
                "code": self.code,
                "message": default_message,
            }
        )


class HTTPNoteRelationCreationError(HTTPBadRequest):
    code = 1003003

    def __init__(self, message: str = None):
        default_message = "NoteRelation creation error"

        if message:
            default_message = f'{default_message}. {message}'

        super().__init__(
            description={
                "code": self.code,
                "message": default_message,
            }
        )


class HTTPNoteRelationRemoveError(HTTPBadRequest):
    code = 1003004

    def __init__(self, message: str = None):
        default_message = "NoteRelation remove error"

        if message:
            default_message = f'{default_message}. {message}'

        super().__init__(
            description={
                "code": self.code,
                "message": default_message,
            }
        )
