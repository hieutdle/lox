from plox.ast_printer import AstPrinter, RpnAstPrinter
from plox.scanner import Token, TokenType
import plox.expr as ast


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


# challenge 3 from http://www.craftinginterpreters.com/representing-code.html#challenges
def test_if_rpn_ast_printer_works_correct() -> None:
    # GIVEN
    # (1 + 2) * (4 - 3)
    expression = ast.Binary(
        ast.Grouping(
            ast.Binary(
                ast.Literal(1),
                Token(TokenType.PLUS, "+", None, 1),
                ast.Literal(2),
            )
        ),
        Token(TokenType.STAR, "*", None, 1),
        ast.Grouping(
            ast.Binary(
                ast.Literal(4),
                Token(TokenType.MINUS, "-", None, 1),
                ast.Literal(3),
            )
        ),
    )
    # WHEN
    result = RpnAstPrinter().print_expr(expression)
    # THEN
    assert result == "1 2 + 4 3 - *"
