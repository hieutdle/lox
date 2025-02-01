import typing
from abc import ABC, abstractmethod
from plox.error import LoxRuntimeError
from plox.stmt import Function
from environment import Environment
from plox.tokens import Token


class LoxCallable(ABC):
    @abstractmethod
    def call(self, interpreter, args) -> typing.Any:
        pass

    @abstractmethod
    def arity(self) -> int:
        pass


class LoxFunction(LoxCallable):
    def __init__(
        self, declaration: Function, closure: Environment, is_init: bool
    ) -> None:
        self.declaration = declaration
        self.closure = closure
        self.is_init = is_init

    def call(self, interpreter, args: list) -> typing.Any:
        env = Environment(self.closure)
        for i in range(len(self.declaration.params)):
            env.define(self.declaration.params[i].lexeme, args[i])
        try:
            interpreter.execute_block(self.declaration.body, env)
        except Return as return_value:
            if self.is_init:
                return self.closure.get_at(0, "this")
            return return_value.value
        if self.is_init:
            return self.closure.get_at(0, "this")
        return None

    def arity(self) -> int:
        return len(self.declaration.params)

    def __str__(self) -> str:
        return f"<fn {self.declaration.name.lexeme}>"

    def bind(self, instance: "LoxInstance") -> "LoxFunction":
        env = Environment(self.closure)
        env.define("this", instance)
        return LoxFunction(self.declaration, env, self.is_init)


class LoxClass(LoxCallable):
    def __init__(
        self,
        name: str,
        superclass: "LoxClass",
        methods: typing.Dict[str, LoxFunction],
    ) -> None:
        self.name = name
        self.superclass = superclass
        self.methods = methods

    def call(self, interpreter, args: list) -> typing.Any:
        instance = LoxInstance(self)
        initializer = self.find_method("init")
        if initializer is not None:
            initializer.bind(instance).call(interpreter, args)
        return instance

    def arity(self) -> int:
        initializer = self.find_method("init")
        if initializer is None:
            return 0
        return initializer.arity()

    def __str__(self) -> str:
        return self.name

    def find_method(self, name: str) -> typing.Optional[LoxFunction]:
        if name in self.methods:
            return self.methods[name]

        if self.superclass is not None:
            return self.superclass.find_method(name)

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
            return method.bind(self)
        raise LoxRuntimeError(name, f"Undefined property {name.lexeme}.")

    def set(self, name: Token, value: typing.Any):
        self.fields[name.lexeme] = value


class Return(RuntimeError):
    def __init__(self, value: typing.Any) -> None:
        self.value = value
