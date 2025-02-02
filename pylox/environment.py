import typing
from pylox.error import LoxRuntimeError
from pylox.tokens import Token


class Environment:
    def __init__(self, enclosing=None) -> None:
        self._values: dict[str, typing.Any] = {}
        self.enclosing = enclosing

    def define(self, name: str, value: typing.Any) -> None:
        self._values[name] = value

    def get(self, name: Token) -> typing.Any:
        if name.lexeme in self._values.keys():
            return self._values[name.lexeme]

        if self.enclosing is not None:
            return self.enclosing.get(name)

        raise LoxRuntimeError(name, f"Undefined variable {name.lexeme}.")

    def assign(self, name: Token, value: typing.Any) -> None:
        if name.lexeme in self._values.keys():
            self._values[name.lexeme] = value
            return

        if self.enclosing is not None:
            self.enclosing.assign(name, value)
            return

        raise LoxRuntimeError(name, f"Undefined variable {name.lexeme}.")

    def get_at(self, distance: int, name: str) -> typing.Any:
        return self.ancestor(distance)._values.get(name)

    def assign_at(self, distance: int, name: Token, value: typing.Any) -> typing.Any:
        self.ancestor(distance)._values[name.lexeme] = value

    def ancestor(self, distance: int) -> typing.Any:
        env = self
        while distance > 0:
            env = env.enclosing  # type: ignore
            distance -= 1
        return env
