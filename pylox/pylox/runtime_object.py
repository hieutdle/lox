import typing
from abc import ABC, abstractmethod


class LoxCallable(ABC):
    @abstractmethod
    def call(self, interpreter, args) -> typing.Any:
        pass

    @abstractmethod
    def arity(self) -> int:
        pass
