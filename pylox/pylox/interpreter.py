import pylox.expr as expr_ast
import pylox.stmt as stmt_ast
import typing
from pylox.error import LoxRuntimeError
from pylox.tokens import Token, TokenType
from pylox.expr import Expr
from pylox.stmt import Stmt
from pylox.environment import Environment


class Interpreter(expr_ast.ExprVisitor):
    def __init__(self):
        self.environment = Environment()

    def interpret(self, statements: list[Stmt]):
        for statement in statements:
            self.execute(statement)

    def execute(self, stmt: Stmt):
        stmt.accept(self)

    def evaluate(self, expr: Expr) -> typing.Any:
        return expr.accept(self)

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
