from ..src.source.currencies_reader import CurrenciesReader
from ..src.lexer.tokens import Tokens
from ..src.source.source import FileSource
from ..src.lexer.lexer import Lexer
from ..src.parser.parser import Parser
from ..src.parser.grammar import *
from ..src.interpreter.scope import *
from ..src.exceptions.exceptions import *
import io
import pytest


def create_interpreter(source_string):
    currencies_reader = CurrenciesReader("resources/currencies.json")
    currencies = currencies_reader.currencies
    for currency in currencies:
        Tokens.keywords[currency.name] = TokenTypes.CURRENCY_TYPE
    parser = create_parser(source_string)
    return Interpreter(parser)


def create_parser(source_string):
    currencies_reader = CurrenciesReader("resources/currencies.json")
    currencies = currencies_reader.currencies
    for currency in currencies:
        Tokens.keywords[currency.name] = TokenTypes.CURRENCY_TYPE
    lexer = Lexer(FileSource(io.StringIO(source_string)))
    return Parser(lexer)


def test_get_currency():
    interpreter = create_interpreter('var.get_currency()')
    get_currency = interpreter.parser.parse_get_currency()
    interpreter.scope_manager.current_scope.add_symbol('var', CurrencyVariable('var', 10, Currency('eur', 1.45)))
    interpreter.visit_get_currency(get_currency)
    assert interpreter.scope_manager.last_result is not None
    assert isinstance(interpreter.scope_manager.last_result, Currency)
    assert interpreter.scope_manager.last_result.name == 'eur'
    assert interpreter.scope_manager.last_result.rate == 1.45


def test_get_currency2():
    interpreter = create_interpreter('var.get_currency()')
    get_currency = interpreter.parser.parse_get_currency()
    interpreter.scope_manager.current_scope.add_symbol('var', DecimalVariable('var', 10))
    with pytest.raises(GetCurrencyError):
        interpreter.visit_get_currency(get_currency)


def test_relational_cond():
    interpreter = create_interpreter('a > b')
    relational_cond = interpreter.parser.parse_relational_cond()
    interpreter.scope_manager.current_scope.add_symbol('a', DecimalVariable('a', 10))
    interpreter.scope_manager.current_scope.add_symbol('b', DecimalVariable('b', 5))
    interpreter.visit_relational_cond(relational_cond)
    assert interpreter.scope_manager.last_result is True


def test_relational_cond2():
    interpreter = create_interpreter('a <= b')
    relational_cond = interpreter.parser.parse_relational_cond()
    interpreter.scope_manager.current_scope.add_symbol('a', DecimalVariable('a', 5))
    interpreter.scope_manager.current_scope.add_symbol('b', DecimalVariable('b', 5))
    interpreter.visit_relational_cond(relational_cond)
    assert interpreter.scope_manager.last_result is True


def test_relational_cond3():  # TODO sprawdzic wynik b * c
    interpreter = create_interpreter('a < b * c')
    relational_cond = interpreter.parser.parse_relational_cond()
    interpreter.scope_manager.current_scope.add_symbol('a', DecimalVariable('a', 3))
    interpreter.scope_manager.current_scope.add_symbol('b', DecimalVariable('b', 2))
    interpreter.scope_manager.current_scope.add_symbol('c', DecimalVariable('c', 2))
    interpreter.visit_relational_cond(relational_cond)
    assert interpreter.scope_manager.last_result is True


def test_equality_cond():
    interpreter = create_interpreter('a == b')
    equality_cond = interpreter.parser.parse_equality_cond()
    interpreter.scope_manager.current_scope.add_symbol('a', DecimalVariable('a', 5))
    interpreter.scope_manager.current_scope.add_symbol('b', DecimalVariable('b', 5))
    interpreter.visit_equality_cond(equality_cond)
    assert interpreter.scope_manager.last_result is True


def test_equality_cond2():
    interpreter = create_interpreter('a != b')
    equality_cond = interpreter.parser.parse_equality_cond()
    interpreter.scope_manager.current_scope.add_symbol('a', DecimalVariable('a', 5))
    interpreter.scope_manager.current_scope.add_symbol('b', DecimalVariable('b', 5))
    interpreter.visit_equality_cond(equality_cond)
    assert interpreter.scope_manager.last_result is False


def test_equality_cond3():
    interpreter = create_interpreter('a == 5')
    equality_cond = interpreter.parser.parse_equality_cond()
    interpreter.scope_manager.current_scope.add_symbol('a', DecimalVariable('a', 5))
    interpreter.visit_equality_cond(equality_cond)
    assert interpreter.scope_manager.last_result is True


def test_and_cond():
    interpreter = create_interpreter('a > b & c == 5')
    and_cond = interpreter.parser.parse_and_cond()
    interpreter.scope_manager.current_scope.add_symbol('a', DecimalVariable('a', 2))
    interpreter.scope_manager.current_scope.add_symbol('b', DecimalVariable('b', 1))
    interpreter.scope_manager.current_scope.add_symbol('c', DecimalVariable('c', 5))
    interpreter.visit_and_cond(and_cond)
    assert interpreter.scope_manager.last_result is True


def test_and_con2():
    interpreter = create_interpreter('a > b & c == 5')
    and_cond = interpreter.parser.parse_and_cond()
    interpreter.scope_manager.current_scope.add_symbol('a', DecimalVariable('a', 2))
    interpreter.scope_manager.current_scope.add_symbol('b', DecimalVariable('b', 2))
    interpreter.scope_manager.current_scope.add_symbol('c', DecimalVariable('c', 5))
    interpreter.visit_and_cond(and_cond)
    assert interpreter.scope_manager.last_result is False


def test_and_cond3():
    interpreter = create_interpreter('a > b & c != 5')
    and_cond = interpreter.parser.parse_and_cond()
    interpreter.scope_manager.current_scope.add_symbol('a', DecimalVariable('a', 2))
    interpreter.scope_manager.current_scope.add_symbol('b', DecimalVariable('b', 1))
    interpreter.scope_manager.current_scope.add_symbol('c', DecimalVariable('c', 5))
    interpreter.visit_and_cond(and_cond)
    assert interpreter.scope_manager.last_result is False


def test_and_cond4():
    interpreter = create_interpreter('a < b & c != 5')
    and_cond = interpreter.parser.parse_and_cond()
    interpreter.scope_manager.current_scope.add_symbol('a', DecimalVariable('a', 2))
    interpreter.scope_manager.current_scope.add_symbol('b', DecimalVariable('b', 1))
    interpreter.scope_manager.current_scope.add_symbol('c', DecimalVariable('c', 5))
    interpreter.visit_and_cond(and_cond)
    assert interpreter.scope_manager.last_result is False


def test_condition():
    interpreter = create_interpreter('a > b | c == 5')
    condition = interpreter.parser.parse_condition()
    interpreter.scope_manager.current_scope.add_symbol('a', DecimalVariable('a', 2))
    interpreter.scope_manager.current_scope.add_symbol('b', DecimalVariable('b', 1))
    interpreter.scope_manager.current_scope.add_symbol('c', DecimalVariable('c', 10))
    interpreter.visit_condition(condition)
    assert interpreter.scope_manager.last_result is True


def test_condition2():
    interpreter = create_interpreter('a < b | c == 5')
    condition = interpreter.parser.parse_condition()
    interpreter.scope_manager.current_scope.add_symbol('a', DecimalVariable('a', 2))
    interpreter.scope_manager.current_scope.add_symbol('b', DecimalVariable('b', 1))
    interpreter.scope_manager.current_scope.add_symbol('c', DecimalVariable('c', 5))
    interpreter.visit_condition(condition)
    assert interpreter.scope_manager.last_result is True


def test_condition3():





    interpreter = create_interpreter('a < b | c == 5')
    condition = interpreter.parser.parse_condition()
    interpreter.scope_manager.current_scope.add_symbol('a', DecimalVariable('a', 2))
    interpreter.scope_manager.current_scope.add_symbol('b', DecimalVariable('b', 1))
    interpreter.scope_manager.current_scope.add_symbol('c', DecimalVariable('c', 10))
    interpreter.visit_condition(condition)
    assert interpreter.scope_manager.last_result is False


def test_condition4():
    interpreter = create_interpreter('a > b & a > c | d == 5')
    condition = interpreter.parser.parse_condition()
    interpreter.scope_manager.current_scope.add_symbol('a', DecimalVariable('a', 2))
    interpreter.scope_manager.current_scope.add_symbol('b', DecimalVariable('b', 1))
    interpreter.scope_manager.current_scope.add_symbol('c', DecimalVariable('c', 10))
    interpreter.scope_manager.current_scope.add_symbol('d', DecimalVariable('d', 10))
    interpreter.visit_condition(condition)
    assert interpreter.scope_manager.last_result is False


def test_condition5():
    interpreter = create_interpreter('a > b & a > c | d == 5')
    condition = interpreter.parser.parse_condition()
    interpreter.scope_manager.current_scope.add_symbol('a', DecimalVariable('a', 2))
    interpreter.scope_manager.current_scope.add_symbol('b', DecimalVariable('b', 1))
    interpreter.scope_manager.current_scope.add_symbol('c', DecimalVariable('c', 10))
    interpreter.scope_manager.current_scope.add_symbol('d', DecimalVariable('d', 5))
    interpreter.visit_condition(condition)
    assert interpreter.scope_manager.last_result is True


def test_condition6():
    interpreter = create_interpreter('a > b & (a > c | d == 5)')
    condition = interpreter.parser.parse_condition()
    interpreter.scope_manager.current_scope.add_symbol('a', DecimalVariable('a', 2))
    interpreter.scope_manager.current_scope.add_symbol('b', DecimalVariable('b', 1))
    interpreter.scope_manager.current_scope.add_symbol('c', DecimalVariable('c', 10))
    interpreter.scope_manager.current_scope.add_symbol('d', DecimalVariable('d', 5))
    interpreter.visit_condition(condition)
    assert interpreter.scope_manager.last_result is True


def test_multipl_expr():
    interpreter = create_interpreter('a * b / c')
    multipl_expr = interpreter.parser.parse_multipl_expr()
    interpreter.scope_manager.current_scope.add_symbol('a', DecimalVariable('a', 3))
    interpreter.scope_manager.current_scope.add_symbol('b', DecimalVariable('b', 4))
    interpreter.scope_manager.current_scope.add_symbol('c', DecimalVariable('c', 2))
    interpreter.visit_multipl_expr(multipl_expr)
    assert isinstance(interpreter.scope_manager.last_result, DecimalVariable)
    assert interpreter.scope_manager.last_result.value == 6


def test_multipl_expr2():
    interpreter = create_interpreter('a * b / c')
    multipl_expr = interpreter.parser.parse_multipl_expr()
    interpreter.scope_manager.current_scope.add_symbol('a', DecimalVariable('a', 3))
    interpreter.scope_manager.current_scope.add_symbol('b', DecimalVariable('b', 4))
    interpreter.scope_manager.current_scope.add_symbol('c', DecimalVariable('c', 0))
    with pytest.raises(DivisionZeroError):
        interpreter.visit_multipl_expr(multipl_expr)


def test_expression():
    interpreter = create_interpreter('a + b - c')
    expression = interpreter.parser.parse_expression()
    interpreter.scope_manager.current_scope.add_symbol('a', DecimalVariable('a', 3))
    interpreter.scope_manager.current_scope.add_symbol('b', DecimalVariable('b', 4))
    interpreter.scope_manager.current_scope.add_symbol('c', DecimalVariable('c', 2))
    interpreter.visit_expression(expression)
    assert isinstance(interpreter.scope_manager.last_result, DecimalVariable)
    assert interpreter.scope_manager.last_result.value == 5


def test_expression2():
    interpreter = create_interpreter('a + b * c')
    expression = interpreter.parser.parse_expression()
    interpreter.scope_manager.current_scope.add_symbol('a', DecimalVariable('a', 3))
    interpreter.scope_manager.current_scope.add_symbol('b', DecimalVariable('b', 5))
    interpreter.scope_manager.current_scope.add_symbol('c', DecimalVariable('c', 6))
    interpreter.visit_expression(expression)
    assert isinstance(interpreter.scope_manager.last_result, DecimalVariable)
    assert interpreter.scope_manager.last_result.value == 33


def test_expression3():
    interpreter = create_interpreter('(a + b) * c')
    expression = interpreter.parser.parse_expression()
    interpreter.scope_manager.current_scope.add_symbol('a', DecimalVariable('a', 3))
    interpreter.scope_manager.current_scope.add_symbol('b', DecimalVariable('b', 5))
    interpreter.scope_manager.current_scope.add_symbol('c', DecimalVariable('c', 6))
    interpreter.visit_expression(expression)
    assert isinstance(interpreter.scope_manager.last_result, DecimalVariable)
    assert interpreter.scope_manager.last_result.value == 48