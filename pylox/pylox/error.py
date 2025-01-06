import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from lox_core import Lox


def error(lox_instance: "Lox", line: int, message: str) -> None:
    report(lox_instance, line, "", message)


def report(lox_instance: "Lox", line: int, where: str, message: str) -> None:
    print(f"[line {line}] Error{where}: {message}", file=sys.stderr)
    lox_instance.had_error = True
