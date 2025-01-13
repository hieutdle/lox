from tokens import Token


class LoxException(BaseException):
    """Base Lox exception type."""

    def __init__(self, line: int, message: str) -> None:
        self.line = line
        self.message = message

    def __str__(self) -> str:
        return f"{type(self).__name__}: Error: {self.message} [line: {self.line}]"


class LoxSyntaxError(LoxException): ...


class LoxParseError(LoxException):
    def __init__(self, token: Token, message: str) -> None:
        self.line = token.line
        self.message = message


class LoxRuntimeError(LoxException):
    def __init__(self, token: Token, message: str) -> None:
        self.line = token.line
        self.message = message
