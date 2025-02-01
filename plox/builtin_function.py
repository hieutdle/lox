import time
from typing import Dict, Any
from plox.runtime_object import LoxCallable


class Clock(LoxCallable):
    def call(self, interpreter, args: Any) -> Any:
        return time.time()

    def arity(self) -> int:
        return 0


class Input(LoxCallable):
    def call(self, interpreter, args: Any) -> Any:
        return input()

    def arity(self) -> int:
        return 0


class Len(LoxCallable):
    def call(self, interpreter, args: Any) -> Any:
        return len(args[0])

    def arity(self) -> int:
        return 1


FUNCTIONS_MAPPING: Dict[str, LoxCallable] = {
    "clock": Clock(),
    "input": Input(),
    "len": Len(),
}
