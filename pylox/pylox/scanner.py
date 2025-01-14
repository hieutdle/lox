from pylox.tokens import Token, TokenType
from pylox.error import LoxSyntaxError
from typing import List, Optional


class Scanner:
    keywords: dict[str, TokenType] = {
        "and": TokenType.AND,
        "class": TokenType.CLASS,
        "else": TokenType.ELSE,
        "false": TokenType.FALSE,
        "for": TokenType.FOR,
        "fun": TokenType.FUN,
        "if": TokenType.IF,
        "nil": TokenType.NIL,
        "or": TokenType.OR,
        "print": TokenType.PRINT,
        "return": TokenType.RETURN,
        "super": TokenType.SUPER,
        "this": TokenType.THIS,
        "true": TokenType.TRUE,
        "var": TokenType.VAR,
        "while": TokenType.WHILE,
    }

    def __init__(self, source: str):
        self.source: str = source
        self.tokens: List[Token] = []
        self.start: int = 0
        self.current: int = 0
        self.line: int = 1

    def scan_tokens(self) -> List[Token]:
        while not self.is_at_end():
            self.start = self.current
            self.scan_token()

        self.tokens.append(Token(TokenType.EOF, "", None, self.line))
        return self.tokens

    def is_at_end(self) -> bool:
        return self.current >= len(self.source)

    def scan_token(self) -> None:
        c = self.advance()
        match c:
            case "(":
                self.add_token(TokenType.LEFT_PAREN)
            case ")":
                self.add_token(TokenType.RIGHT_PAREN)
            case "{":
                self.add_token(TokenType.LEFT_BRACE)
            case "}":
                self.add_token(TokenType.RIGHT_BRACE)
            case ",":
                self.add_token(TokenType.COMMA)
            case ".":
                self.add_token(TokenType.DOT)
            case "-":
                self.add_token(TokenType.MINUS)
            case "+":
                self.add_token(TokenType.PLUS)
            case ";":
                self.add_token(TokenType.SEMICOLON)
            case "*":
                self.add_token(TokenType.STAR)
            case "!":
                self.add_token(
                    TokenType.BANG_EQUAL if self.match("=") else TokenType.BANG
                )
            case "=":
                self.add_token(
                    TokenType.EQUAL_EQUAL if self.match("=") else TokenType.EQUAL
                )
            case "<":
                self.add_token(
                    TokenType.LESS_EQUAL if self.match("=") else TokenType.LESS
                )
            case ">":
                self.add_token(
                    TokenType.GREATER_EQUAL if self.match("=") else TokenType.GREATER
                )
            case "/":
                if self.match("*"):
                    self.block_comment()
                elif self.match("/"):
                    while self.peek() != "\n" and not self.is_at_end():
                        self.advance()
                else:
                    self.add_token(TokenType.SLASH)
            case " " | "\r" | "\t":
                # Ignore whitespace
                pass
            case "\n":
                self.line += 1
            case '"':
                self.string()
            case _ if self.is_digit(c):
                self.number()
            case _ if self.is_alpha(c):
                self.identifier()
            case _:
                raise LoxSyntaxError(self.line, "Unexpected character.")

    def advance(self) -> str:
        char: str = self.source[self.current]
        self.current += 1
        return char

    def add_token(
        self, token_type: TokenType, literal: Optional[object] = None
    ) -> None:
        text: str = self.source[self.start : self.current]
        self.tokens.append(Token(token_type, text, literal, self.line))

    def match(self, expected: str) -> bool:
        if self.is_at_end():
            return False
        if self.source[self.current] != expected:
            return False
        self.current += 1
        return True

    def peek(self) -> str:
        if self.is_at_end():
            return "\0"
        return self.source[self.current]

    def string(self):
        # Handle comment
        while self.peek() != '"' and not self.is_at_end():
            if self.peek() == "\n":
                self.line += 1
            self.advance()

        if self.is_at_end():
            raise LoxSyntaxError(self.line, "Unterminated string.")

        # Consume the closing ".
        self.advance()

        # Extract the string value, excluding the surrounding quotes.
        value: str = self.source[self.start + 1 : self.current - 1]
        self.add_token(TokenType.STRING, value)

    @staticmethod
    def is_digit(c: str) -> bool:
        return "0" <= c <= "9"

    def peek_next(self) -> str:
        if self.current + 1 >= len(self.source):
            return "\0"
        return self.source[self.current + 1]

    def number(self) -> None:
        # Consume the integer part
        while self.is_digit(self.peek()):
            self.advance()

        # Check for a fractional part
        if self.peek() == "." and self.is_digit(self.peek_next()):
            # Consume the "."
            self.advance()

            # Consume the fractional part
            while self.is_digit(self.peek()):
                self.advance()

            # Convert the lexeme to a float and add it as a token
            value: float = float(self.source[self.start : self.current])
            self.add_token(TokenType.NUMBER, value)
        else:
            # Convert the lexeme to an int and add it as a token
            value: int = int(self.source[self.start : self.current])
            self.add_token(TokenType.NUMBER, value)

    def identifier(self) -> None:
        while self.is_alpha_numeric(self.peek()):
            self.advance()

        # Get the full lexeme of the identifier or keyword
        text: str = self.source[self.start : self.current]

        # Check if the lexeme is a reserved word; if not, it's an identifier
        token_type: TokenType = self.keywords.get(text, TokenType.IDENTIFIER)
        self.add_token(token_type)

    @staticmethod
    def is_alpha(c: str) -> bool:
        return ("a" <= c <= "z") or ("A" <= c <= "Z") or c == "_"

    def is_alpha_numeric(self, c: str) -> bool:
        return self.is_alpha(c) or self.is_digit(c)

    def block_comment(self) -> None:
        depth: int = 1

        while depth != 0:
            if self.is_at_end():
                # Unterminated block comment
                raise LoxSyntaxError(
                    self.line,
                    "Unterminated block comment.",
                )

            if self.peek() == "*" and self.peek_next() == "/":
                depth -= 1
                self.advance()
                self.advance()
            elif self.peek() == "/" and self.peek_next() == "*":
                depth += 1
                self.advance()
                self.advance()
            else:
                if self.peek() == "\n":
                    self.line += 1
                self.advance()
