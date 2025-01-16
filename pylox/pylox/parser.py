from typing import List, Optional, Callable
from pylox.tokens import Token, TokenType
from pylox.expr import Expr
import pylox.expr as expr_ast
from pylox.error import LoxParseError
from pylox.stmt import Stmt
import pylox.stmt as stmt_ast
import typing


# recursive descent, top-down parser
class Parser:
    def __init__(
        self, tokens: List[Token], report_error: Optional[Callable] = None
    ) -> None:
        self.tokens = tokens
        self.current = 0
        self.errors = []
        self.report_error = report_error
        self.allow_expressions = False
        self.found_expression = False

    def parse_repl(self) -> typing.Any:
        try:
            self.allow_expressions = True
            statements: list[Stmt] = []
            while not self.is_at_end():
                parsed = self.declaration()
                if parsed is not None:
                    statements.append(parsed)
                if self.found_expression and isinstance(
                    statements[-1], stmt_ast.Expression
                ):
                    last: stmt_ast.Expression = statements[-1]
                    return last.expression
                elif self.found_expression:
                    raise RuntimeError("Unexpected situation -- panic mode")
            return statements
        finally:
            self.allow_expressions = False
            self.found_expression = False

    # program        → declaration * EOF;
    def parse(self) -> list[Stmt]:
        statements: list[Stmt] = []
        while not self.is_at_end():
            parsed = self.declaration()
            if parsed is not None:
                statements.append(parsed)

        return statements

    # declaration → varDecl
    #             | statement ;

    def declaration(self) -> Optional[Stmt]:
        try:
            if self.match(TokenType.VAR):
                return self.var_declaration()
            return self.statement()
        except LoxParseError:
            self.synchronize()
            return None

    # varDecl        → "var" IDENTIFIER ( "=" expression )? ";" ;
    def var_declaration(self) -> Stmt:
        name = self.consume(TokenType.IDENTIFIER, "Expect variable name.")
        initializer: Optional[Expr] = None

        if self.match(TokenType.EQUAL):
            initializer = self.expression()

        self.consume(TokenType.SEMICOLON, "Expect ';' after variable declaration.")

        return stmt_ast.Var(name, initializer)

    # statement  → exprStmt
    #            | printStmt ;
    #            | block ;
    def statement(self) -> Stmt:
        if self.match(TokenType.PRINT):
            return self.print_statement()

        if self.match(TokenType.LEFT_BRACE):
            return stmt_ast.Block(self.block())

        return self.expression_statement()

    # block          → "{" declaration* "}" ;
    def block(self) -> List[Stmt]:
        stmts: List[Stmt] = []
        while not self.check(TokenType.RIGHT_BRACE) and not self.is_at_end():
            result = self.declaration()
            if result is not None:
                stmts.append(result)
        self.consume(TokenType.RIGHT_BRACE, "Expect '}' after block.")
        return stmts

    # printStmt      → "print" expression ";" ;
    def print_statement(self) -> Stmt:
        value = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after value.")
        return stmt_ast.Print(value)

    # exprStmt       → expression ";" ;
    def expression_statement(self) -> Stmt:
        value = self.expression()
        if self.allow_expressions and self.is_at_end():
            self.found_expression = True
        else:
            self.consume(TokenType.SEMICOLON, "Expect ';' after value.")
        return stmt_ast.Expression(value)

    # expression     → assignment;
    def expression(self) -> Expr:
        return self.assignment()

    # assignment     → IDENTIFIER "=" assignment
    #                | equality ;
    def assignment(self) -> Expr:
        expr = self.equality()
        if self.match(TokenType.EQUAL):
            equals = self.previous()
            value = self.assignment()
            if isinstance(expr, expr_ast.Variable):
                name = expr.name
                return expr_ast.Assign(name, value)
            else:
                self.error(equals, "Invalid assignment target.")
        return expr

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

    # primary        → NUMBER | STRING | "true" | "false" | "nil" | "(" expression ")" | IDENTIFIER ;
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

        if self.match(TokenType.IDENTIFIER):
            return expr_ast.Variable(self.previous())

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

    def error(self, token: Token, msg: str) -> LoxParseError:
        err = LoxParseError(token, msg)
        self.errors.append(err)
        if self.report_error is not None:
            self.report_error(err)
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
