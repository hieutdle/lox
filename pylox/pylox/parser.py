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
        self.loop_depth = 0

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
    #            | ifStmt
    #            | printStmt
    #            | whileStmt
    #            | block ;
    def statement(self) -> Stmt:
        if self.match(TokenType.IF):
            return self.if_statement()
        if self.match(TokenType.PRINT):
            return self.print_statement()
        if self.match(TokenType.WHILE):
            return self.while_statement()
        if self.match(TokenType.LEFT_BRACE):
            return stmt_ast.Block(self.block())
        if self.match(TokenType.FOR):
            return self.for_statement()
        if self.match(TokenType.BREAK):
            return self.break_statement()

        return self.expression_statement()

    # break -> 'break' ;
    def break_statement(self) -> Stmt:
        if self.loop_depth == 0:
            self.error(self.previous(), "Must be inside a loop to use 'break'.")

        self.consume(TokenType.SEMICOLON, "Expect ';' after 'break'.")
        return stmt_ast.Break()

    # forStmt        → "for" "(" ( varDecl | exprStmt | ";" )
    #                  expression? ";"
    #                  expression? ")" statement ;
    def for_statement(self) -> Stmt:
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after 'for'.")
        initializer = None
        if self.match(TokenType.SEMICOLON):
            pass
        elif self.match(TokenType.VAR):
            initializer = self.var_declaration()
        else:
            initializer = self.expression_statement()
        condition = None
        if not self.check(TokenType.SEMICOLON):
            condition = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after loop condition.")
        increment = None
        if not self.check(TokenType.RIGHT_PAREN):
            increment = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after for clauses.")

        try:
            self.loop_depth += 1
            body = self.statement()

            if increment is not None:
                body = stmt_ast.Block([body, stmt_ast.Expression(increment)])

            if condition is None:
                condition = expr_ast.Literal(True)

            result: stmt_ast.While | stmt_ast.Block = stmt_ast.While(condition, body)
            if initializer is not None:
                result = stmt_ast.Block([initializer, result])

            return result
        finally:
            self.loop_depth -= 1

    # whileStmt      → "while" "(" expression ")" statement ;
    def while_statement(self) -> Stmt:
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after 'while'.")
        condition = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after condition.")
        try:
            self.loop_depth += 1
            body = self.statement()
            return stmt_ast.While(condition, body)
        finally:
            self.loop_depth -= 1

    # ifStmt         → "if" "(" expression ")" statement
    #            ( "else" statement )? ;
    def if_statement(self) -> Stmt:
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after 'if'.")
        condition = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after if condition.")
        then_branch = self.statement()
        else_branch = None
        if self.match(TokenType.ELSE):
            else_branch = self.statement()
        return stmt_ast.If(condition, then_branch, else_branch)

    # block          → "{" declaration* "}" ;
    def block(self) -> typing.List[Stmt]:
        stmts: typing.List[Stmt] = []
        while not self.check(TokenType.RIGHT_BRACE) and not self.is_at_end():
            result = self.declaration()
            if result is not None:
                stmts.append(result)
        self.consume(TokenType.RIGHT_BRACE, "Expect '}' after block.")
        return stmts

    # printStmt      → "print" expression ";" ;
    def print_statement(self) -> Stmt:
        value = self.expression()
        self.consume(TokenType.SEMICOLON, "printStmt: Expect ';' after value.")
        return stmt_ast.Print(value)

    # exprStmt       → expression ";" ;
    def expression_statement(self) -> Stmt:
        value = self.expression()
        if self.allow_expressions and self.is_at_end():
            self.found_expression = True
        else:
            self.consume(TokenType.SEMICOLON, "exprStmt: Expect ';' after value.")
        return stmt_ast.Expression(value)

    # expression     → assignment;
    def expression(self) -> Expr:
        return self.assignment()

    # assignment     → IDENTIFIER "=" assignment
    #                | logic_or ;
    def assignment(self) -> Expr:
        expr = self.or_expression()
        if self.match(TokenType.EQUAL):
            equals = self.previous()
            value = self.assignment()
            if isinstance(expr, expr_ast.Variable):
                name = expr.name
                return expr_ast.Assign(name, value)
            else:
                self.error(equals, "Invalid assignment target.")
        return expr

    # logic_or       → logic_and ( "or" logic_and )* ;

    def or_expression(self) -> Expr:
        expr = self.and_expression()
        while self.match(TokenType.OR):
            op = self.previous()
            right = self.and_expression()
            expr = expr_ast.Logical(expr, op, right)
        return expr

    # logic_and      → equality ( "and" equality )* ;
    def and_expression(self) -> Expr:
        expr = self.equality()
        while self.match(TokenType.AND):
            op = self.previous()
            right = self.equality()
            expr = expr_ast.Logical(expr, op, right)
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

    # unary          → ( "!" | "-" ) unary | call ;
    def unary(self) -> Expr:
        if self.match(TokenType.BANG, TokenType.MINUS):
            op = self.previous()
            right = self.unary()
            return expr_ast.Unary(op, right)

        return self.call()

    # call           → primary ( "(" arguments? ")" )* ;
    def call(self) -> Expr:
        expr = self.primary()
        while True:
            if self.match(TokenType.LEFT_PAREN):
                expr = self.parse_arguments(expr)
            else:
                break
        return expr

    # arguments      → expression ( "," expression )* ;
    def parse_arguments(self, callee: Expr) -> Expr:
        arguments: typing.List[Expr] = []
        if not self.check(TokenType.RIGHT_PAREN):
            is_comma = True
            while is_comma:
                if len(arguments) >= 255:
                    raise self.error(self.peek(), "Can't have more than 255 arguments.")
                arguments.append(self.expression())
                is_comma = self.match(TokenType.COMMA)
        paren = self.consume(TokenType.RIGHT_PAREN, "Expect ')' after arguments.")
        return expr_ast.Call(callee, paren, arguments)

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
                    TokenType.BREAK,
                ):
                    return

            self.advance()
