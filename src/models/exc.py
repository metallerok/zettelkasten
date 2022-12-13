class AttributeValidationError(AttributeError):
    def __init__(self, message: str = None, *args):
        self.message = message

        super().__init__(*args)
