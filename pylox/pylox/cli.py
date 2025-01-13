import sys
from scanner import Scanner


class Lox:
    had_error: bool = False

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
            if not line:
                break
            self.run(line)
            Lox.had_error = False  # Reset error flag after each prompt

    def run_file(self, filename: str) -> None:
        with open(filename, encoding="utf-8") as f:
            content: str = f.read()
        self.run(content)

        if self.had_error:
            sys.exit(65)

    @staticmethod
    def run(source: str) -> None:
        scanner: Scanner = Scanner(source)
        tokens = scanner.scan_tokens()

        for token in tokens:
            print(token)


if __name__ == "__main__":
    lox = Lox()
    lox.main()
