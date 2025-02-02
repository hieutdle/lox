# THIS CODE IS GENERATED AUTOMATICALLY. DO NOT CHANGE IT MANUALLY!

import typing
from abc import ABC, abstractmethod

from pylox.expr import Expr, Variable

from pylox.tokens import Token


class StmtVisitor(ABC):
    @abstractmethod
    def visit_if_stmt(self, stmt) -> typing.Any:
        pass

    @abstractmethod
    def visit_block_stmt(self, stmt) -> typing.Any:
        pass

    @abstractmethod
    def visit_expression_stmt(self, stmt) -> typing.Any:
        pass

    @abstractmethod
    def visit_print_stmt(self, stmt) -> typing.Any:
        pass

    @abstractmethod
    def visit_var_stmt(self, stmt) -> typing.Any:
        pass

    @abstractmethod
    def visit_while_stmt(self, stmt) -> typing.Any:
        pass

    @abstractmethod
    def visit_break_stmt(self, stmt) -> typing.Any:
        pass

    @abstractmethod
    def visit_function_stmt(self, stmt) -> typing.Any:
        pass

    @abstractmethod
    def visit_return_stmt(self, stmt) -> typing.Any:
        pass

    @abstractmethod
    def visit_class_stmt(self, stmt) -> typing.Any:
        pass


class Stmt(ABC):
    @abstractmethod
    def accept(self, visitor: StmtVisitor) -> typing.Any:
        pass


class If(Stmt):
    def __init__(
        self, condition: Expr, then_branch: Stmt, else_branch: typing.Optional[Stmt]
    ):
        self.condition = condition
        self.then_branch = then_branch
        self.else_branch = else_branch

    def accept(self, visitor: StmtVisitor) -> typing.Any:
        return visitor.visit_if_stmt(self)


class Block(Stmt):
    def __init__(self, statements: typing.List[Stmt]):
        self.statements = statements

    def accept(self, visitor: StmtVisitor) -> typing.Any:
        return visitor.visit_block_stmt(self)


class Expression(Stmt):
    def __init__(self, expression: Expr):
        self.expression = expression

    def accept(self, visitor: StmtVisitor) -> typing.Any:
        return visitor.visit_expression_stmt(self)


class Print(Stmt):
    def __init__(self, expression: Expr):
        self.expression = expression

    def accept(self, visitor: StmtVisitor) -> typing.Any:
        return visitor.visit_print_stmt(self)


class Var(Stmt):
    def __init__(self, name: Token, initializer: typing.Optional[Expr]):
        self.name = name
        self.initializer = initializer

    def accept(self, visitor: StmtVisitor) -> typing.Any:
        return visitor.visit_var_stmt(self)


class While(Stmt):
    def __init__(self, condition: Expr, body: Stmt):
        self.condition = condition
        self.body = body

    def accept(self, visitor: StmtVisitor) -> typing.Any:
        return visitor.visit_while_stmt(self)


class Break(Stmt):
    def __init__(self):
        super().__init__()

    def accept(self, visitor: StmtVisitor) -> typing.Any:
        return visitor.visit_break_stmt(self)


class Function(Stmt):
    def __init__(
        self, name: Token, params: typing.List[Token], body: typing.List[Stmt]
    ):
        self.name = name
        self.params = params
        self.body = body

    def accept(self, visitor: StmtVisitor) -> typing.Any:
        return visitor.visit_function_stmt(self)


class Return(Stmt):
    def __init__(self, keyword: Token, value: typing.Optional[Expr]):
        self.keyword = keyword
        self.value = value

    def accept(self, visitor: StmtVisitor) -> typing.Any:
        return visitor.visit_return_stmt(self)


class Class(Stmt):
    def __init__(
        self,
        name: Token,
        superclass: typing.Optional[Variable],
        methods: typing.List[Function],
    ):
        self.name = name
        self.superclass = superclass
        self.methods = methods

    def accept(self, visitor: StmtVisitor) -> typing.Any:
        return visitor.visit_class_stmt(self)
