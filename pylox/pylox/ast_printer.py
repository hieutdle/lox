from pylox.expr import Expr, Binary, Grouping, Literal, Unary, ExprVisitor
from pylox.tokens import Token, TokenType


class AstPrinter(ExprVisitor):
    def print(self, expr: Expr) -> str:
        return expr.accept(self)

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


if __name__ == "__main__":
    expression = Binary(
        Unary(Token(TokenType.MINUS, "-", None, 1), Literal(123)),
        Token(TokenType.STAR, "*", None, 1),
        Grouping(Literal(45.67)),
    )
    printer = AstPrinter()
    print(printer.print(expression))  # Expected output: (* (- 123) (group 45.67))
