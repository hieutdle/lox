from enum import Enum, auto
import typing

from pylox.error import LoxParseError
from pylox.expr import (
    Assign,
    Binary,
    Call,
    Expr,
    ExprVisitor,
    Grouping,
    Literal,
    Logical,
    Unary,
    Variable,
)
from pylox.interpreter import Interpreter
from pylox.stmt import (
    Block,
    Class,
    Expression,
    Function,
    If,
    Print,
    Return,
    Stmt,
    StmtVisitor,
    Var,
    While,
)
from pylox.tokens import Token


class FunctionType(Enum):
    NONE = (auto(),)
    FUNCTION = auto()


class Resolver(ExprVisitor, StmtVisitor):
    def __init__(self, interpreter: Interpreter):
        self.interpreter = interpreter
        self.scopes: typing.List[typing.Dict[str, bool]] = []
        self.current_function = FunctionType.NONE

    def visit_class_stmt(self, stmt: Class) -> typing.Any:
        self.declare(stmt.name)
        self.define(stmt.name)
        return None

    def visit_var_stmt(self, stmt: Var) -> typing.Any:
        self.declare(stmt.name)
        if stmt.initializer is not None:
            self.resolve_ast_node(stmt.initializer)
        self.define(stmt.name)
        return None

    def visit_assign_expr(self, expr: Assign) -> typing.Any:
        self.resolve_ast_node(expr.value)
        self.resolve_local(expr, expr.name)
        return None

    def visit_if_stmt(self, stmt: If) -> typing.Any:
        self.resolve_ast_node(stmt.condition)
        self.resolve_ast_node(stmt.then_branch)
        if stmt.else_branch is not None:
            self.resolve_ast_node(stmt.else_branch)
        return None

    def visit_call_expr(self, expr: Call) -> typing.Any:
        self.resolve_ast_node(expr.callee)
        for arg in expr.arguments:
            self.resolve_ast_node(arg)
        return None

    def visit_grouping_expr(self, expr: Grouping) -> typing.Any:
        self.resolve_ast_node(expr.expression)
        return None

    def visit_literal_expr(self, expr: Literal) -> typing.Any:
        # do nothing
        return None

    def visit_logical_expr(self, expr: Logical) -> typing.Any:
        self.resolve_ast_node(expr.left)
        self.resolve_ast_node(expr.right)
        return None

    def visit_unary_expr(self, expr: Unary) -> typing.Any:
        self.resolve_ast_node(expr.right)
        return None

    def visit_function_stmt(self, stmt: Function) -> typing.Any:
        self.declare(stmt.name)
        # Unlike variables, though, we define the name eagerly,
        # before resolving the function’s body.
        # This lets a function recursively refer to itself inside its own body.
        self.define(stmt.name)
        self.resolve_function(stmt, FunctionType.FUNCTION)
        return None

    def visit_binary_expr(self, expr: Binary) -> typing.Any:
        self.resolve_ast_node(expr.left)
        self.resolve_ast_node(expr.right)
        return None

    def visit_while_stmt(self, stmt: While) -> typing.Any:
        self.resolve_ast_node(stmt.condition)
        self.resolve_ast_node(stmt.body)
        return None

    def visit_print_stmt(self, stmt: Print) -> typing.Any:
        self.resolve_ast_node(stmt.expression)
        return None

    def visit_return_stmt(self, stmt: Return) -> typing.Any:
        if self.current_function is FunctionType.NONE:
            raise LoxParseError(stmt.keyword, "Can't return from top-level code.")
        if stmt.value is not None:
            self.resolve_ast_node(stmt.value)
        return None

    def resolve_function(self, function: Function, fun_type: FunctionType) -> None:
        parent_fun = self.current_function
        self.current_function = fun_type
        self.begin_scope()
        for param in function.params:
            self.declare(param)
            self.define(param)
        self.resolve(function.body)
        self.end_scope()
        self.current_function = parent_fun

    def visit_expression_stmt(self, stmt: Expression) -> typing.Any:
        self.resolve_ast_node(stmt.expression)
        return None

    def visit_variable_expr(self, expr: Variable) -> typing.Any:
        #  If the variable exists in the current scope but its value is false,
        #  that means we have declared it but not yet defined it.
        #  We report that error.
        if len(self.scopes) > 0 and self.scopes[-1].get(expr.name.lexeme) is False:
            raise LoxParseError(
                expr.name, "Can't read local variable in its own initializer."
            )
        self.resolve_local(expr, expr.name)
        return None

    def declare(self, identifier: Token) -> None:
        if len(self.scopes) == 0:
            return
        scope = self.scopes[-1]
        scope[identifier.lexeme] = False

    def define(self, identifier: Token) -> None:
        if len(self.scopes) == 0:
            return
        scope = self.scopes[-1]
        scope[identifier.lexeme] = True

    def visit_block_stmt(self, stmt: Block) -> typing.Any:
        self.begin_scope()
        self.resolve(stmt.statements)
        self.end_scope()
        return None

    def resolve(self, statements: list[Stmt]) -> None:
        for statement in statements:
            self.resolve_ast_node(statement)

    def resolve_ast_node(self, node: Stmt | Expr) -> None:
        node.accept(self)

    def begin_scope(self) -> None:
        self.scopes.append({})

    def end_scope(self) -> None:
        self.scopes.pop()

    def visit_break_stmt(self, stmt) -> typing.Any:
        return None

    # We start at the innermost scope and work outwards, looking in each map for a matching name.
    # If we find the variable, we resolve it
    # passing in the number of scopes between the current innermost scope and the scope where the variable was found
    def resolve_local(self, expr: Expr, name: Token) -> None:
        for i in range(len(self.scopes) - 1, -1, -1):
            if name.lexeme in self.scopes[i].keys():
                self.interpreter.resolve(expr, len(self.scopes) - 1 - i)
                return
