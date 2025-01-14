from pylox.ast_printer import AstPrinter
from pylox.scanner import Token, TokenType
import pylox.expr as ast


# example from http://www.craftinginterpreters.com/representing-code.html#a-not-very-pretty-printer
def test_if_ast_printer_works_correct() -> None:
    # GIVEN
    # -123 * (45.67)
    expression = ast.Binary(
        ast.Unary(Token(TokenType.MINUS, "-", None, 1), ast.Literal(123)),
        Token(TokenType.STAR, "*", None, 1),
        ast.Grouping(ast.Literal(45.67)),
    )

    # WHEN
    result = AstPrinter().print(expression)

    # THEN
    assert result == "(* (- 123) (group 45.67))"
