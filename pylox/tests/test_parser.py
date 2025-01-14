import pytest

from pylox.ast_printer import AstPrinter
from pylox.parser import Parser
from pylox.scanner import Scanner
from pylox.error import LoxParseError


def test_if_parser_produces_valid_ast() -> None:
    # GIVEN
    src = "-123 * (45.67)"
    # WHEN
    tokens = Scanner(src).scan_tokens()
    ast = Parser(tokens).expression()
    result = AstPrinter().print(ast)
    # THEN
    assert result == "(* (- 123) (group 45.67))"


def test_if_parser_handles_unclosed_paren() -> None:
    # GIVEN
    src = "-123 * (45.67"
    # WHEN
    tokens = Scanner(src).scan_tokens()
    with pytest.raises(LoxParseError) as err:
        Parser(tokens).expression()
    # THEN
    assert "Expect ')' after expression." in err.value.message


def test_if_parser_handles_empty_right_hand_operand_inside_binary_expression() -> None:
    # GIVEN
    src = "123 * "
    # WHEN
    tokens = Scanner(src).scan_tokens()
    with pytest.raises(LoxParseError) as err:
        Parser(tokens).expression()
    # THEN
    assert "Expect expression" in err.value.message


def test_if_parser_handles_empty_left_hand_operand_inside_binary_expression() -> None:
    # GIVEN
    src = "* 123"
    # WHEN
    tokens = Scanner(src).scan_tokens()
    with pytest.raises(LoxParseError) as err:
        Parser(tokens).expression()
    # THEN
    assert "Missing left-hand operand." in err.value.message


def test_if_parser_parse_and_discard_right_hand_operand_in_case_of_empty_left_hand_operant() -> (
    None
):
    # GIVEN
    src = "* (123"
    tokens = Scanner(src).scan_tokens()

    with pytest.raises(LoxParseError) as err:
        Parser(tokens).expression()

    # THEN
    assert "Expect ')' after expression." in err.value.message
