from pylox.expr import Expr, Binary, Grouping, Literal, Unary, ExprVisitor
from pylox.tokens import Token, TokenType
import typing


class AstPrinter(ExprVisitor):
    def print(self, expr: Expr) -> str:
        return expr.accept(self)

    def visit_call_expr(self, expr: Expr) -> typing.Any:
        pass

    def visit_logical_expr(self, expr: Expr) -> typing.Any:
        pass

    def visit_assign_expr(self, expr: Expr) -> typing.Any:
        pass

    def visit_variable_expr(self, expr: Expr) -> typing.Any:
        pass

    def visit_get_expr(self, expr) -> typing.Any:
        pass

    def visit_set_expr(self, expr) -> typing.Any:
        pass

    def visit_binary_expr(self, expr: Binary) -> str:
        return self.parenthesize(expr.operator.lexeme, expr.left, expr.right)

    def visit_grouping_expr(self, expr: Grouping) -> str:
        return self.parenthesize("group", expr.expression)

    def visit_literal_expr(self, expr: Literal) -> str:
        return "nil" if expr.value is None else str(expr.value)

    def visit_unary_expr(self, expr: Unary) -> str:
        return self.parenthesize(expr.operator.lexeme, expr.right)

    def parenthesize(self, name: str, *exprs: Expr) -> str:
        result: str = f"({name}"
        for expr in exprs:
            result += " " + expr.accept(self)
        result += ")"
        return result


# In reverse Polish notation (RPN),
# the operands to an arithmetic operator are both placed before the operator,
# so 1 + 2 becomes 1 2 +
# Define a visitor class for our syntax tree classes that takes an expression,
# converts it to RPN, and returns the resulting string.
class RpnAstPrinter(ExprVisitor):
    def visit_get_expr(self, expr) -> typing.Any:
        pass

    def visit_set_expr(self, expr) -> typing.Any:
        pass

    def visit_call_expr(self, expr: Expr) -> typing.Any:
        pass

    def visit_logical_expr(self, expr: Expr) -> typing.Any:
        pass

    def visit_assign_expr(self, expr: Expr) -> typing.Any:
        pass

    def visit_variable_expr(self, expr: Expr) -> typing.Any:
        pass

    def print_expr(self, expr: Expr):
        return expr.accept(self)

    def visit_binary_expr(self, expr: Binary):
        return f"{str(expr.left.accept(self))} {str(expr.right.accept(self))} {expr.operator.lexeme}"

    def visit_grouping_expr(self, expr: Grouping):
        return expr.expression.accept(self)

    def visit_literal_expr(self, expr: Literal):
        return str(expr.value)

    def visit_unary_expr(self, expr: Unary):
        op = expr.operator.lexeme
        if op == "-":
            # Can't use same symbol for unary and binary.
            op = "~"
        return f"{str(expr.right.accept(self))} {op}"


if __name__ == "__main__":
    expression = Binary(
        Unary(Token(TokenType.MINUS, "-", None, 1), Literal(123)),
        Token(TokenType.STAR, "*", None, 1),
        Grouping(Literal(45.67)),
    )
    printer = AstPrinter()
    print(printer.print(expression))  # Expected output: (* (- 123) (group 45.67))
