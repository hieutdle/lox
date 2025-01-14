import pylox.expr as ast
import typing
from error import LoxRuntimeError
from tokens import Token, TokenType


class Interpreter(ast.ExprVisitor):
    def evaluate(self, expr: ast.Expr) -> typing.Any:
        return expr.accept(self)

    def visit_literal_expr(self, expr: ast.Literal) -> typing.Any:
        return expr.value

    def visit_grouping_expr(self, expr: ast.Grouping) -> typing.Any:
        return self.evaluate(expr.expression)

    def visit_unary_expr(self, expr: ast.Unary) -> typing.Any:
        right = self.evaluate(expr.right)

        match expr.operator.token_type:
            case TokenType.MINUS:
                self.check_number_operand(expr.operator, right)
                return -float(right)
            case TokenType.BANG:
                return not self.is_truthy(right)
            case _:
                return None  # Fallback case

    def visit_binary_expr(self, expr: ast.Binary) -> typing.Any:
        left = self.evaluate(expr.left)
        right = self.evaluate(expr.right)

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

                if type(left) is str and type(right) is str:
                    return left + right

                raise LoxRuntimeError(
                    expr.operator,
                    "Operands must be two numbers of two strings.",
                )
        return None  # Fallback case

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
