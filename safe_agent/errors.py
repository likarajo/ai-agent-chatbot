class Refusal(Exception):
    """The question cannot be answered from the published schema."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class UnsafeSQL(Exception):
    """A statement failed the query check and must not run."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message
