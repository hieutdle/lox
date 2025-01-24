import typing
from abc import ABC, abstractmethod
from pylox.stmt import Function
from environment import Environment


class LoxCallable(ABC):
    @abstractmethod
    def call(self, interpreter, args) -> typing.Any:
        pass

    @abstractmethod
    def arity(self) -> int:
        pass


class LoxFunction(LoxCallable):
    def __init__(self, declaration: Function):
        self._declaration = declaration

    def call(self, interpreter, args: list) -> typing.Any:
        env = Environment(interpreter.globals)
        for i in range(len(self._declaration.params)):
            env.define(self._declaration.params[i].lexeme, args[i])
        try:
            interpreter.execute_block(self._declaration.body, env)
        except Return as return_value:
            return return_value.value
        return None

    def arity(self) -> int:
        return len(self._declaration.params)

    def __str__(self):
        return f"<fn {self._declaration.name.lexeme}>"


class Return(RuntimeError):
    def __init__(self, value: typing.Any) -> None:
        self.value = value
