import typing
from pylox.error import LoxRuntimeError
from pylox.tokens import Token


class Environment:
    def __init__(self) -> None:
        self._values: dict[str, typing.Any] = {}

    def define(self, name: str, value: typing.Any) -> None:
        self._values[name] = value

    def get(self, name: Token) -> typing.Any:
        if name.lexeme in self._values.keys():
            return self._values[name.lexeme]
        raise LoxRuntimeError(name, f"Undefined variable {name.lexeme}.")

    def assign(self, name: Token, value: typing.Any) -> None:
        if name.lexeme in self._values.keys():
            self._values[name.lexeme] = value
            return
        raise LoxRuntimeError(name, f"Undefined variable {name.lexeme}.")
