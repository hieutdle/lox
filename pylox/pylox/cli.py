import sys
from pylox.scanner import Scanner
from pylox.error import LoxException, LoxRuntimeError, LoxParseError, LoxSyntaxError
from pylox.interpreter import Interpreter
from pylox.parser import Parser
import typing


class Lox:
    def __init__(self) -> None:
        self.interpreter = Interpreter()
        self.had_error: bool = False
        self.had_runtime_error: bool = False

    def main(self) -> None:
        arg_count: int = len(sys.argv)
        if arg_count == 1:
            self.run_prompt()
        elif arg_count == 2:
            self.run_file(sys.argv[1])
        else:
            print("Usage: pylox [script]")
            sys.exit(64)

    def run_prompt(self) -> None:
        while True:
            line: str = input("> ")
            if not line or line.lower() == "exit":
                break
            try:
                self.run(line)
            except LoxParseError as e:
                self.report_error(e)
            except LoxRuntimeError as e:
                self.report_runtime_error(e)

            # Reset error flag after each prompt
            Lox.had_error = False
            Lox.had_runtime_error = False

    def run_file(self, filename: str) -> None:
        with open(filename, encoding="utf-8") as f:
            content: str = f.read()
        self.run(content)

        if self.had_error:
            sys.exit(65)

        if self.had_runtime_error:
            sys.exit(70)

    def run(self, source: str) -> None:
        try:
            scanner: Scanner = Scanner(source)
            tokens = scanner.scan_tokens()
            # print("Tokens:", [(token.lexeme, token.token_type) for token in tokens])
            ast = Parser(tokens).parse()
            print(self.interpreter.interpret(ast))
        except LoxSyntaxError as e:
            self.report_error(e)
        except LoxParseError as e:
            self.report_error(e)
        except LoxRuntimeError as e:
            self.report_runtime_error(e)

    @staticmethod
    def stringify(value: typing.Any) -> str:
        if value is None:
            return "nil"

        if type(value) is float and float(value).is_integer():
            return str(int(value))

        return str(value)

    @staticmethod
    def _build_error_string(err: LoxException) -> str:
        return f"line {err.line + 1}: Error: {err.message}"

    def report_error(self, err: LoxException) -> None:
        print(self._build_error_string(err))
        self.had_error = True

    def report_runtime_error(self, err: LoxRuntimeError) -> None:
        print(self._build_error_string(err))
        self.had_error = True
        self.had_runtime_error = True


if __name__ == "__main__":
    lox = Lox()
    lox.main()
