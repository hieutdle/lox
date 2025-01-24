import pylox.expr as expr_ast
import pylox.stmt as stmt_ast
import typing
from pylox.error import LoxRuntimeError, BreakException
from pylox.tokens import Token, TokenType
from pylox.expr import Expr
from pylox.stmt import Stmt
from pylox.environment import Environment
from pylox.runtime_object import LoxCallable, LoxFunction, Return
from pylox.builtin_function import FUNCTIONS_MAPPING


class Interpreter(expr_ast.ExprVisitor, stmt_ast.StmtVisitor):
    def __init__(self):
        self.globals = Environment()
        self.environment = self.globals
        self.init_standard_library()

    def init_standard_library(self):
        for name, func in FUNCTIONS_MAPPING.items():
            self.globals.define(name, func)

    def interpret(self, statements: list[Stmt]):
        for statement in statements:
            self.execute(statement)

    def interpret_expr(self, expr: Expr) -> str:
        return self.stringify(self.evaluate(expr))

    def execute(self, stmt: Stmt):
        stmt.accept(self)

    def evaluate(self, expr: Expr) -> typing.Any:
        return expr.accept(self)

    def visit_return_stmt(self, stmt: stmt_ast.Return) -> typing.Any:
        value = None
        if stmt.value is not None:
            value = self.evaluate(stmt.value)
        raise Return(value)

    def visit_function_stmt(self, stmt: stmt_ast.Function) -> typing.Any:
        function = LoxFunction(stmt, self.environment)
        self.environment.define(stmt.name.lexeme, function)
        return None

    def visit_call_expr(self, expr: expr_ast.Call) -> typing.Any:
        callee = self.evaluate(expr.callee)
        arguments: list = []
        for arg in expr.arguments:
            arguments.append(self.evaluate(arg))
        if not isinstance(callee, LoxCallable):
            raise LoxRuntimeError(expr.paren, "Can only call functions and classes.")
        if len(arguments) != callee.arity():
            raise LoxRuntimeError(
                expr.paren,
                f"Expected {callee.arity()} arguments but got {len(arguments)}.",
            )
        return callee.call(self, arguments)

    def visit_logical_expr(self, expr: expr_ast.Logical) -> typing.Any:
        left = self.evaluate(expr.left)
        if expr.operator.token_type == TokenType.OR:
            if self.is_truthy(left):
                return left
        elif expr.operator.token_type == TokenType.AND:
            if not self.is_truthy(left):
                return left
        return self.evaluate(expr.right)

    def visit_while_stmt(self, stmt: stmt_ast.While) -> typing.Any:
        try:
            while self.is_truthy(self.evaluate(stmt.condition)):
                self.execute(stmt.body)
        except BreakException:
            pass  # Do nothing.

    def visit_break_stmt(self, stmt) -> typing.Any:
        raise BreakException()

    def visit_if_stmt(self, stmt: stmt_ast.If) -> typing.Any:
        if self.is_truthy(self.evaluate(stmt.condition)):
            self.execute(stmt.then_branch)
        elif stmt.else_branch is not None:
            self.execute(stmt.else_branch)
        return None

    def visit_block_stmt(self, stmt: stmt_ast.Block) -> typing.Any:
        self.execute_block(stmt.statements, Environment(self.environment))
        return None

    def execute_block(self, statements: typing.List[Stmt], env: Environment) -> None:
        previous = self.environment
        try:
            self.environment = env
            for stmt in statements:
                self.execute(stmt)
        finally:
            self.environment = previous

    def visit_var_stmt(self, stmt: stmt_ast.Var) -> typing.Any:
        value: typing.Any = None
        if stmt.initializer is not None:
            value = self.evaluate(stmt.initializer)
        self.environment.define(stmt.name.lexeme, value)
        return None

    def visit_assign_expr(self, expr: expr_ast.Assign) -> typing.Any:
        value = self.evaluate(expr.value)
        self.environment.assign(expr.name, value)
        return value

    def visit_variable_expr(self, expr: expr_ast.Variable) -> typing.Any:
        return self.environment.get(expr.name)

    def visit_expression_stmt(self, stmt: stmt_ast.Expression) -> typing.Any:
        self.evaluate(stmt.expression)
        return None

    def visit_print_stmt(self, stmt: stmt_ast.Print) -> typing.Any:
        value = self.evaluate(stmt.expression)
        print(self.stringify(value))
        return None

    def visit_literal_expr(self, expr: expr_ast.Literal) -> typing.Any:
        return expr.value

    def visit_grouping_expr(self, expr: expr_ast.Grouping) -> typing.Any:
        return self.evaluate(expr.expression)

    def visit_unary_expr(self, expr: expr_ast.Unary) -> typing.Any:
        right = self.evaluate(expr.right)

        match expr.operator.token_type:
            case TokenType.MINUS:
                self.check_number_operand(expr.operator, right)
                return -float(right)
            case TokenType.BANG:
                return not self.is_truthy(right)
            case _:
                return None  # Fallback case

    def visit_binary_expr(self, expr: expr_ast.Binary) -> typing.Any:
        left = self.evaluate(expr.left)
        right = self.evaluate(expr.right)

        # print(f"Operator: {expr.operator.token_type}, Expected: {TokenType.PLUS}")
        # print(f"ID of expr.operator.token_type: {id(expr.operator.token_type)}")
        # print(f"ID of TokenType.PLUS: {id(TokenType.PLUS)}")
        # ID of expr.operator.token_type: 140211793605728
        # ID of TokenType.PLUS: 140211793606544
        # Ensure correct, consistent import
        # from pylox.tokens import TokenType
        # not from tokens import TokenType

        match expr.operator.token_type:
            case TokenType.GREATER:
                self.check_number_operands(expr.operator, left, right)
                return float(left) > float(right)
            case TokenType.GREATER_EQUAL:
                self.check_number_operands(expr.operator, left, right)
                return float(left) >= float(right)
            case TokenType.LESS:
                self.check_number_operands(expr.operator, left, right)
                return float(left) < float(right)
            case TokenType.LESS_EQUAL:
                self.check_number_operands(expr.operator, left, right)
                return float(left) <= float(right)
            case TokenType.MINUS:
                self.check_number_operands(expr.operator, left, right)
                return float(left) - float(right)
            case TokenType.SLASH:
                self.check_number_operands(expr.operator, left, right)
                if float(right) == 0:
                    raise LoxRuntimeError(
                        expr.operator,
                        "Division by zero!",
                    )
                return float(left) / float(right)
            case TokenType.STAR:
                self.check_number_operands(expr.operator, left, right)
                return float(left) * float(right)
            case TokenType.BANG_EQUAL:
                return left != right
            case TokenType.EQUAL_EQUAL:
                return left == right
            case TokenType.PLUS:
                if self.is_number(left) and self.is_number(right):
                    return float(left) + float(right)

                if type(left) is str or type(right) is str:
                    return self.stringify(left) + self.stringify(right)

                raise LoxRuntimeError(
                    expr.operator,
                    "Operands must be two numbers or two strings.",
                )
        return "abc"

    @staticmethod
    def is_truthy(object: typing.Any) -> bool:
        if object is None:
            return False
        elif type(object) is bool:
            return bool(object)
        else:
            return True

    @staticmethod
    def is_number(value: typing.Any) -> bool:
        return (type(value) is int) or (type(value) is float)

    @staticmethod
    def check_number_operand(op: Token, operand: typing.Any) -> None:
        if Interpreter.is_number(operand):
            return
        raise LoxRuntimeError(op, "Operand must be a number.")

    @staticmethod
    def check_number_operands(op: Token, left, right: typing.Any) -> None:
        if Interpreter.is_number(left) and Interpreter.is_number(right):
            return
        raise LoxRuntimeError(op, "Operands must be a numbers.")

    @staticmethod
    def stringify(value: typing.Any) -> str:
        if value is None:
            return "nil"
        if type(value) is float and float(value).is_integer():
            return str(int(value))
        if type(value) is bool:
            return str(value).lower()

        return str(value)
