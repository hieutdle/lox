import typing
from abc import ABC, abstractmethod
from pylox.error import LoxRuntimeError
from pylox.stmt import Function
from environment import Environment
from pylox.tokens import Token


class LoxCallable(ABC):
    @abstractmethod
    def call(self, interpreter, args) -> typing.Any:
        pass

    @abstractmethod
    def arity(self) -> int:
        pass


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


class LoxClass(LoxCallable):
    def __init__(self, name: str, methods: typing.Dict[str, LoxFunction]) -> None:
        self.name = name
        self.methods = methods

    def call(self, interpreter, args: list) -> typing.Any:
        return LoxInstance(self)

    def arity(self) -> int:
        return 0

    def __str__(self) -> str:
        return self.name

    def find_method(self, name: str) -> typing.Optional[LoxFunction]:
        if name in self.methods:
            return self.methods[name]
        return None


class LoxInstance:
    def __init__(self, lox_class: LoxClass) -> None:
        self.lox_class = lox_class
        self.fields: typing.Dict[str, typing.Any] = {}

    def __str__(self) -> str:
        return f"{self.lox_class.name} instance"

    def get(self, name: Token):
        if name.lexeme in self.fields:
            return self.fields.get(name.lexeme)
        method = self.lox_class.find_method(name.lexeme)
        if method is not None:
            return method
        raise LoxRuntimeError(name, f"Undefined property {name.lexeme}.")

    def set(self, name: Token, value: typing.Any):
        self.fields[name.lexeme] = value


class Return(RuntimeError):
    def __init__(self, value: typing.Any) -> None:
        self.value = value
