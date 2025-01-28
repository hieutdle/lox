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


class LoxClass:
    def __init__(self, name: str):
        self.name = name

    def __str__(self):
        return self.name


class LoxFunction(LoxCallable):
    def __init__(self, declaration: Function, closure: Environment):
        self.declaration = declaration
        self.closure = closure

    def call(self, interpreter, args: list) -> typing.Any:
        env = Environment(self.closure)
        for i in range(len(self.declaration.params)):
            env.define(self.declaration.params[i].lexeme, args[i])
        try:
            interpreter.execute_block(self.declaration.body, env)
        except Return as return_value:
            return return_value.value
        return None

    def arity(self) -> int:
        return len(self.declaration.params)

    def __str__(self):
        return f"<fn {self.declaration.name.lexeme}>"


class Return(RuntimeError):
    def __init__(self, value: typing.Any) -> None:
        self.value = value
