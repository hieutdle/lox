from typing import List
from pylox.tokens import Token, TokenType
from pylox.expr import Expr
import pylox.expr as expr_ast
from pylox.error import LoxParseError


# recursive descent, top-down parser
class Parser:
    def __init__(self, tokens: List[Token]) -> None:
        self.tokens = tokens
        self.current = 0
        self.errors = []  # Store errors instead of raising immediately

    def parse(self) -> Expr:
        try:
            return self.expression()
        except LoxParseError as e:
            return e

    # expression     → equality
    def expression(self) -> Expr:
        return self.equality()

    # equality       → comparison ( ( "!=" | "==" ) comparison )* ;
    def equality(self) -> Expr:
        expr = self.comparison()

        while self.match(TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL):
            op = self.previous()
            right = self.comparison()
            expr = expr_ast.Binary(expr, op, right)

        return expr

    # comparison     → term ( ( ">" | ">=" | "<" | "<=" ) term )* ;
    def comparison(self) -> Expr:
        expr = self.term()

        while self.match(
            TokenType.GREATER,
            TokenType.GREATER_EQUAL,
            TokenType.LESS,
            TokenType.LESS_EQUAL,
        ):
            op = self.previous()
            right = self.term()
            expr = expr_ast.Binary(expr, op, right)

        return expr

    # term           → factor ( ( "-" | "+" ) factor )* ;
    def term(self) -> Expr:
        expr = self.factor()

        while self.match(TokenType.MINUS, TokenType.PLUS):
            op = self.previous()
            right = self.factor()
            expr = expr_ast.Binary(expr, op, right)
            # print(f"Created Binary Node: {expr}")

        return expr

    # factor         → unary ( ( "/" | "*" ) unary )* ;
    def factor(self) -> Expr:
        expr = self.unary()

        while self.match(TokenType.SLASH, TokenType.STAR):
            op = self.previous()
            right = self.unary()
            expr = expr_ast.Binary(expr, op, right)

        return expr

    # unary          → ( "!" | "-" ) unary | primary ;
    def unary(self) -> Expr:
        if self.match(TokenType.BANG, TokenType.MINUS):
            op = self.previous()
            right = self.unary()
            return expr_ast.Unary(op, right)

        return self.primary()

    # primary        → NUMBER | STRING | "true" | "false" | "nil" | "(" expression ")" ;
    def primary(self) -> Expr:
        if self.match(TokenType.FALSE):
            return expr_ast.Literal(False)

        if self.match(TokenType.TRUE):
            return expr_ast.Literal(True)

        if self.match(TokenType.NIL):
            return expr_ast.Literal(None)

        if self.match(TokenType.NUMBER, TokenType.STRING):
            return expr_ast.Literal(self.previous().literal)

        if self.match(TokenType.LEFT_PAREN):
            expr = self.expression()
            self.consume(TokenType.RIGHT_PAREN, "Expect ')' after expression.")
            return expr_ast.Grouping(expr)

        # Error handling
        if self.match(TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL):
            err = self.error(self.previous(), "Missing left-hand operand.")
            self.equality()
            raise err

        if self.match(TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL):
            err = self.error(self.previous(), "Missing left-hand operand.")
            self.equality()
            raise err

        if self.match(
            TokenType.GREATER,
            TokenType.GREATER_EQUAL,
            TokenType.LESS,
            TokenType.LESS_EQUAL,
        ):
            err = self.error(self.previous(), "Missing left-hand operand.")
            self.comparison()
            raise err

        if self.match(TokenType.PLUS):
            err = self.error(self.previous(), "Missing left-hand operand.")
            self.term()
            raise err

        if self.match(TokenType.SLASH, TokenType.STAR):
            err = self.error(self.previous(), "Missing left-hand operand.")
            self.factor()
            raise err

        raise self.error(self.peek(), "Expect expression")

    # helpers
    def match(self, *token_types: TokenType) -> bool:
        for token_type in token_types:
            if self.check(token_type):
                self.advance()
                return True
        return False

    def check(self, token_type: TokenType) -> bool:
        if self.is_at_end():
            return False
        return self.peek().token_type == token_type

    def advance(self) -> Token:
        if not self.is_at_end():
            self.current += 1
        return self.previous()

    def is_at_end(self) -> bool:
        return self.peek().token_type == TokenType.EOF

    def peek(self) -> Token:
        return self.tokens[self.current]

    def previous(self) -> Token:
        return self.tokens[self.current - 1]

    # error handling
    def consume(self, token_type: TokenType, message: str) -> Token:
        if self.check(token_type):
            return self.advance()

        raise self.error(self.peek(), message)

    def error(self, token: Token, message: str) -> Exception:
        err = LoxParseError(token, message)
        self.errors.append(err)

        return err

    def synchronize(self) -> None:
        self.advance()

        while not self.is_at_end():
            if self.previous().token_type == TokenType.SEMICOLON:
                return

            match self.peek().token_type:
                case (
                    TokenType.CLASS,
                    TokenType.FUN,
                    TokenType.VAR,
                    TokenType.FOR,
                    TokenType.IF,
                    TokenType.WHILE,
                    TokenType.PRINT,
                    TokenType.RETURN,
                ):
                    return

            self.advance()
