import io
import pytest
from ..src.lexer.lexer import Lexer
from ..src.lexer.token import TokenTypes
from ..src.lexer.tokens import Tokens
from ..src.source.currencies_reader import CurrenciesReader
from ..src.source.source import FileSource
from ..src.exceptions.exceptions import *


def create_lexer(source_string):
    currencies_reader = CurrenciesReader("resources/currencies.json")
    currencies = currencies_reader.currencies
    for currency in currencies:
        Tokens.keywords[currency] = TokenTypes.CURRENCY_TYPE
    return Lexer(FileSource(io.StringIO(source_string)))


def test_eof():
    lexer = create_lexer("")

    lexer.get_next_token()
    assert lexer.token.type == TokenTypes.EOT


def test_identifier1():
    lexer = create_lexer("identifier")

    lexer.get_next_token()
    assert lexer.token.type == TokenTypes.IDENTIFIER
    assert lexer.token.value == "identifier"

    lexer.get_next_token()
    assert lexer.token.type == TokenTypes.EOT
    assert lexer.token.value is None


def test_identifier2():
    lexer = create_lexer("id_ent1if_ier2")

    lexer.get_next_token()
    assert lexer.token.type == TokenTypes.IDENTIFIER
    assert lexer.token.value == "id_ent1if_ier2"


def test_identifier3():
    lexer = create_lexer("id_ent1??if_ier2")

    lexer.get_next_token()
    assert lexer.token.type == TokenTypes.IDENTIFIER
    assert lexer.token.value == "id_ent1"

    with pytest.raises(InvalidTokenError):
        lexer.get_next_token()


def test_too_long_token():
    file_text = 51 * 'a'
    lexer = create_lexer(file_text)

    with pytest.raises(TokenTooLongError):
        lexer.get_next_token()


def test_int():
    lexer = create_lexer("123")

    lexer.get_next_token()
    assert lexer.token.type == TokenTypes.NUMBER
    assert lexer.token.value == "123"
    assert lexer.token.numerical_value == 123

    lexer.get_next_token()
    assert lexer.token.type == TokenTypes.EOT
    assert lexer.token.value is None


def test_float():
    lexer = create_lexer("123.45")

    lexer.get_next_token()
    assert lexer.token.type == TokenTypes.NUMBER
    assert lexer.token.value == "123.45"
    assert lexer.token.numerical_value == 123.45


def test_float2():
    lexer = create_lexer("123.45000")

    lexer.get_next_token()
    assert lexer.token.type == TokenTypes.NUMBER
    assert lexer.token.value == "123.45000"
    assert lexer.token.numerical_value == 123.45


def test_numbers_with_chars():
    lexer = create_lexer("123abc")

    lexer.get_next_token()
    assert lexer.token.type == TokenTypes.NUMBER
    assert lexer.token.value == "123"
    assert lexer.token.numerical_value == 123

    lexer.get_next_token()
    assert lexer.token.type == TokenTypes.IDENTIFIER
    assert lexer.token.value == "abc"


def test_fract_less_than_1():
    lexer = create_lexer("0.45")

    lexer.get_next_token()
    assert lexer.token.type == TokenTypes.NUMBER
    assert lexer.token.value == "0.45"
    assert lexer.token.numerical_value == 0.45


def test_fract_with_0():
    lexer = create_lexer("123.045")

    lexer.get_next_token()
    assert lexer.token.type == TokenTypes.NUMBER
    assert lexer.token.value == "123.045"
    assert lexer.token.numerical_value == 123.045


def test_negative_float():
    lexer = create_lexer("-123.45")

    lexer.get_next_token()
    assert lexer.token.type == TokenTypes.MINUS

    lexer.get_next_token()
    assert lexer.token.type == TokenTypes.NUMBER
    assert lexer.token.value == "123.45"
    assert lexer.token.numerical_value == 123.45


def test_zero():
    lexer = create_lexer("0")

    lexer.get_next_token()
    assert lexer.token.type == TokenTypes.NUMBER
    assert lexer.token.value == "0"
    assert lexer.token.numerical_value == 0


def test_number_with_too_many_dots():
    lexer = create_lexer("123.45.67")

    lexer.get_next_token()
    assert lexer.token.type == TokenTypes.NUMBER
    assert lexer.token.value == "123.45"
    assert lexer.token.numerical_value == 123.45


def test_string1():
    lexer = create_lexer('"abcd123"')

    lexer.get_next_token()
    assert lexer.token.type == TokenTypes.STRING
    assert lexer.token.value == '"abcd123"'


def test_too_long_string():
    file_text = '"' + 1001 * 'a' + '"'
    lexer = create_lexer(file_text)

    with pytest.raises(StringTooLongError):
        lexer.get_next_token()


# ------------KEYWORDS------------

def test_keyword_if():
    lexer = create_lexer("if")

    lexer.get_next_token()
    assert lexer.token.type == TokenTypes.IF


def test_keyword_else():
    lexer = create_lexer("else")

    lexer.get_next_token()
    assert lexer.token.type == TokenTypes.ELSE


def test_keyword_while():
    lexer = create_lexer("while")

    lexer.get_next_token()
    assert lexer.token.type == TokenTypes.WHILE


def test_keyword_return():
    lexer = create_lexer("return")

    lexer.get_next_token()
    assert lexer.token.type == TokenTypes.RETURN


def test_keyword_dec():
    lexer = create_lexer("dec")

    lexer.get_next_token()
    assert lexer.token.type == TokenTypes.DECIMAL


def test_keyword_cur():
    lexer = create_lexer("cur")

    lexer.get_next_token()
    assert lexer.token.type == TokenTypes.CURRENCY


def test_keyword_print():
    lexer = create_lexer("print")

    lexer.get_next_token()
    assert lexer.token.type == TokenTypes.PRINT


def test_keyword_get_currency():
    lexer = create_lexer("get_currency")

    lexer.get_next_token()
    assert lexer.token.type == TokenTypes.GET_CURRENCY


# ------------SINGLE OPERATORS------------

def test_single_operator_op_bracket():
    lexer = create_lexer("(")

    lexer.get_next_token()
    assert lexer.token.type == TokenTypes.OP_BRACKET


def test_single_operator_cl_bracket():
    lexer = create_lexer(")")

    lexer.get_next_token()
    assert lexer.token.type == TokenTypes.CL_BRACKET


def test_single_operator_op_curly_bracket():
    lexer = create_lexer("{")

    lexer.get_next_token()
    assert lexer.token.type == TokenTypes.OP_CURLY_BRACKET


def test_single_operator_cl_curly_bracket():
    lexer = create_lexer("}")

    lexer.get_next_token()
    assert lexer.token.type == TokenTypes.CL_CURLY_BRACKET


def test_single_operator_op_square_bracket():
    lexer = create_lexer("[")

    lexer.get_next_token()
    assert lexer.token.type == TokenTypes.OP_SQUARE_BRACKET


def test_single_operator_cl_square_bracket():
    lexer = create_lexer("]")

    lexer.get_next_token()
    assert lexer.token.type == TokenTypes.CL_SQUARE_BRACKET


def test_single_operator_plus():
    lexer = create_lexer("+")

    lexer.get_next_token()
    assert lexer.token.type == TokenTypes.PLUS


def test_single_operator_minus():
    lexer = create_lexer("-")

    lexer.get_next_token()
    assert lexer.token.type == TokenTypes.MINUS


def test_single_operator_multiply():
    lexer = create_lexer("*")

    lexer.get_next_token()
    assert lexer.token.type == TokenTypes.MULTIPLY


def test_single_operator_divide():
    lexer = create_lexer("/")

    lexer.get_next_token()
    assert lexer.token.type == TokenTypes.DIVIDE


def test_single_operator_assignment():
    lexer = create_lexer("=")

    lexer.get_next_token()
    assert lexer.token.type == TokenTypes.ASSIGNMENT


def test_single_operator_greater_than():
    lexer = create_lexer(">")

    lexer.get_next_token()
    assert lexer.token.type == TokenTypes.GREATER_THAN


def test_single_operator_less_than():
    lexer = create_lexer("<")

    lexer.get_next_token()
    assert lexer.token.type == TokenTypes.LESS_THAN


def test_single_operator_comma():
    lexer = create_lexer(",")

    lexer.get_next_token()
    assert lexer.token.type == TokenTypes.COMMA


def test_single_operator_semicolon():
    lexer = create_lexer(";")

    lexer.get_next_token()
    assert lexer.token.type == TokenTypes.SEMICOLON


def test_single_operator_dot():
    lexer = create_lexer(".")

    lexer.get_next_token()
    assert lexer.token.type == TokenTypes.DOT


def test_single_operator_underline():
    lexer = create_lexer("_")

    lexer.get_next_token()
    assert lexer.token.type == TokenTypes.UNDERLINE


def test_single_operator_not():
    lexer = create_lexer("!")

    lexer.get_next_token()
    assert lexer.token.type == TokenTypes.NOT


def test_single_operator_and():
    lexer = create_lexer("&")

    lexer.get_next_token()
    assert lexer.token.type == TokenTypes.AND


def test_single_operator_or():
    lexer = create_lexer("|")

    lexer.get_next_token()
    assert lexer.token.type == TokenTypes.OR


def test_double_operator_equal():
    lexer = create_lexer("==")

    lexer.get_next_token()
    assert lexer.token.type == TokenTypes.EQUAL


def test_double_operator_not_equal():
    lexer = create_lexer("!=")

    lexer.get_next_token()
    assert lexer.token.type == TokenTypes.NOT_EQUAL


def test_double_operator_greater_or_equal():
    lexer = create_lexer(">=")

    lexer.get_next_token()
    assert lexer.token.type == TokenTypes.GREATER_OR_EQUAL


def test_double_operator_less_or_equal():
    lexer = create_lexer("<=")

    lexer.get_next_token()
    assert lexer.token.type == TokenTypes.LESS_OR_EQUAL


def test_comment():
    lexer = create_lexer("a = b # comment \n dec = 0.5")

    lexer.get_next_token()
    assert lexer.token.type == TokenTypes.IDENTIFIER
    assert lexer.token.value == "a"

    lexer.get_next_token()
    assert lexer.token.type == TokenTypes.ASSIGNMENT

    lexer.get_next_token()
    assert lexer.token.type == TokenTypes.IDENTIFIER
    assert lexer.token.value == "b"

    lexer.get_next_token()
    assert lexer.token.type == TokenTypes.DECIMAL


def test_fake_comment():
    lexer = create_lexer('"abc#d"')

    lexer.get_next_token()
    assert lexer.token.type == TokenTypes.STRING
    assert lexer.token.value == '"abc#d"'


def test_tokens_lines():
    lexer = create_lexer("a + b    \n print   \n   \nreturn")

    lexer.get_next_token()
    assert lexer.token.line == 1

    lexer.get_next_token()
    assert lexer.token.line == 1

    lexer.get_next_token()
    assert lexer.token.line == 1

    lexer.get_next_token()
    assert lexer.token.line == 2

    lexer.get_next_token()
    assert lexer.token.line == 4


def test_tokens_columns():
    lexer = create_lexer("a + b\n print\n\n return")

    lexer.get_next_token()
    assert lexer.token.column == 1

    lexer.get_next_token()
    assert lexer.token.column == 3

    lexer.get_next_token()
    assert lexer.token.column == 5

    lexer.get_next_token()
    assert lexer.token.column == 2

    lexer.get_next_token()
    assert lexer.token.column == 2


def test_get_currency_operation():
    lexer = create_lexer("a.get_currency()")

    lexer.get_next_token()
    assert lexer.token.type == TokenTypes.IDENTIFIER
    assert lexer.token.value == "a"

    lexer.get_next_token()
    assert lexer.token.type == TokenTypes.DOT

    lexer.get_next_token()
    assert lexer.token.type == TokenTypes.GET_CURRENCY

    lexer.get_next_token()
    assert lexer.token.type == TokenTypes.OP_BRACKET

    lexer.get_next_token()
    assert lexer.token.type == TokenTypes.CL_BRACKET


def test_print_operation1():
    lexer = create_lexer('print("abcd")')

    lexer.get_next_token()
    assert lexer.token.type == TokenTypes.PRINT

    lexer.get_next_token()
    assert lexer.token.type == TokenTypes.OP_BRACKET

    lexer.get_next_token()
    assert lexer.token.type == TokenTypes.STRING
    assert lexer.token.value == '"abcd"'

    lexer.get_next_token()
    assert lexer.token.type == TokenTypes.CL_BRACKET


def test_print_operation2():
    lexer = create_lexer('print("abcd", id1, id2)')

    lexer.get_next_token()
    assert lexer.token.type == TokenTypes.PRINT

    lexer.get_next_token()
    assert lexer.token.type == TokenTypes.OP_BRACKET

    lexer.get_next_token()
    assert lexer.token.type == TokenTypes.STRING
    assert lexer.token.value == '"abcd"'

    lexer.get_next_token()
    assert lexer.token.type == TokenTypes.COMMA

    lexer.get_next_token()
    assert lexer.token.type == TokenTypes.IDENTIFIER
    assert lexer.token.value == "id1"

    lexer.get_next_token()
    assert lexer.token.type == TokenTypes.COMMA

    lexer.get_next_token()
    assert lexer.token.type == TokenTypes.IDENTIFIER
    assert lexer.token.value == "id2"

    lexer.get_next_token()
    assert lexer.token.type == TokenTypes.CL_BRACKET


def test_invalid_token_error1():
    lexer = create_lexer(" @ ")

    with pytest.raises(InvalidTokenError):
        lexer.get_next_token()


def test_invalid_token_error2():
    lexer = create_lexer("$id1")

    with pytest.raises(InvalidTokenError):
        lexer.get_next_token()


def test_pln():
    lexer = create_lexer("pln")

    lexer.get_next_token()
    assert lexer.token.type == TokenTypes.CURRENCY_TYPE
    assert lexer.token.value == "pln"


def test_pln_with_parameter():
    lexer = create_lexer("pln id1")

    lexer.get_next_token()
    assert lexer.token.type == TokenTypes.CURRENCY_TYPE
    assert lexer.token.value == "pln"

    lexer.get_next_token()
    assert lexer.token.type == TokenTypes.IDENTIFIER
    assert lexer.token.value == "id1"


def test_pln_with_expression():
    lexer = create_lexer("pln a + b")

    lexer.get_next_token()
    assert lexer.token.type == TokenTypes.CURRENCY_TYPE
    assert lexer.token.value == "pln"

    lexer.get_next_token()
    assert lexer.token.type == TokenTypes.IDENTIFIER
    assert lexer.token.value == "a"

    lexer.get_next_token()
    assert lexer.token.type == TokenTypes.PLUS

    lexer.get_next_token()
    assert lexer.token.type == TokenTypes.IDENTIFIER
    assert lexer.token.value == "b"
