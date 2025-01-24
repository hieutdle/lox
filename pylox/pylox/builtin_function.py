import time
import typing
from pylox.runtime_object import LoxCallable


class Clock(LoxCallable):
    def call(self, interpreter, args) -> typing.Any:
        return time.time()

    def arity(self) -> int:
        return 0


FUNCTIONS_MAPPING = {
    "clock": Clock(),
}
