from ..src.lexer.tokens import Tokens
from ..src.source.source import FileSource
from ..src.lexer.lexer import Lexer
from ..src.parser.parser import Parser
from ..src.parser.grammar import *
from ..src.interpreter.scope import *
from ..src.exceptions.exceptions import *
from ..src.source.currencies_reader import CurrenciesReader
from ..src.source.currencies import Currencies
import io
import pytest


def create_interpreter(source_string):
    CurrenciesReader("resources/currencies.json")
    currencies = Currencies.currencies
    for currency in currencies:
        Tokens.keywords[currency] = TokenTypes.CURRENCY_TYPE
    lexer = Lexer(FileSource(io.StringIO(source_string)))
    parser = Parser(lexer)
    return Interpreter(parser)


def set_currencies():
    Currencies.currencies = {
        "pln": {
            "chf": 1,
            "gbd": 2,
            "usd": 3,
            "eur": 4
        },
        "chf": {
            "pln": 5,
            "gbd": 6,
            "usd": 7,
            "eur": 8
        },
        "gbd": {
            "pln": 9,
            "chf": 10,
            "usd": 11,
            "eur": 12
        },
        "usd": {
            "pln": 13,
            "chf": 14,
            "gbd": 15,
            "eur": 16
        },
        "eur": {
            "pln": 17,
            "chf": 18,
            "gbd": 19,
            "usd": 20
        }
    }


def test_get_currency():
    interpreter = create_interpreter('var.get_currency()')
    get_currency = interpreter.parser.parse_get_currency()
    interpreter.scope_manager.current_scope.add_symbol('var', CurrencyVariable('var', 10, 'eur'))
    interpreter.visit_get_currency(get_currency)
    assert interpreter.scope_manager.last_result is not None
    assert interpreter.scope_manager.last_result == 'eur'


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


def test_relational_cond3():
    interpreter = create_interpreter('a < b * c')
    relational_cond = interpreter.parser.parse_relational_cond()
    interpreter.scope_manager.current_scope.add_symbol('a', DecimalVariable('a', 3))
    interpreter.scope_manager.current_scope.add_symbol('b', DecimalVariable('b', 2))
    interpreter.scope_manager.current_scope.add_symbol('c', DecimalVariable('c', 2))
    interpreter.visit_relational_cond(relational_cond)
    assert interpreter.scope_manager.last_result is True


def test_relational_cond_with_not():
    interpreter = create_interpreter('! a > b')
    relational_cond = interpreter.parser.parse_relational_cond()
    interpreter.scope_manager.current_scope.add_symbol('a', DecimalVariable('a', 3))
    interpreter.scope_manager.current_scope.add_symbol('b', DecimalVariable('b', 5))
    interpreter.visit_relational_cond(relational_cond)
    assert interpreter.scope_manager.last_result is True


def test_relational_cond_with_not2():
    interpreter = create_interpreter('! a < b')
    relational_cond = interpreter.parser.parse_relational_cond()
    interpreter.scope_manager.current_scope.add_symbol('a', DecimalVariable('a', 8))
    interpreter.scope_manager.current_scope.add_symbol('b', DecimalVariable('b', 5))
    interpreter.visit_relational_cond(relational_cond)
    assert interpreter.scope_manager.last_result is True


def test_relational_cond_with_not3():
    interpreter = create_interpreter('! a >= b')
    relational_cond = interpreter.parser.parse_relational_cond()
    interpreter.scope_manager.current_scope.add_symbol('a', DecimalVariable('a', 3))
    interpreter.scope_manager.current_scope.add_symbol('b', DecimalVariable('b', 5))
    interpreter.visit_relational_cond(relational_cond)
    assert interpreter.scope_manager.last_result is True


def test_relational_cond_with_not4():
    interpreter = create_interpreter('! a <= b')
    relational_cond = interpreter.parser.parse_relational_cond()
    interpreter.scope_manager.current_scope.add_symbol('a', DecimalVariable('a', 8))
    interpreter.scope_manager.current_scope.add_symbol('b', DecimalVariable('b', 5))
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


def test_equality_cond_with_not():
    interpreter = create_interpreter('! a == 5')
    equality_cond = interpreter.parser.parse_equality_cond()
    interpreter.scope_manager.current_scope.add_symbol('a', DecimalVariable('a', 6))
    interpreter.visit_equality_cond(equality_cond)
    assert interpreter.scope_manager.last_result is True


def test_equality_cond_with_not2():
    interpreter = create_interpreter('! a != 5')
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


def test_expression4():
    interpreter = create_interpreter('2 + 5')
    expression = interpreter.parser.parse_expression()
    interpreter.visit_expression(expression)
    assert isinstance(interpreter.scope_manager.last_result, DecimalVariable)
    assert interpreter.scope_manager.last_result.value == 7


def test_print_statement():
    interpreter = create_interpreter('print("result: ", 2 + 2);')
    print_statement = interpreter.parser.parse_print_statement()
    interpreter.visit_print_statement(print_statement)
    assert interpreter.scope_manager.last_result == 'result: 4.0'


def test_print_statement2():
    interpreter = create_interpreter('print("result: ", 2 + 2, " is correct. ", a - b);')
    print_statement = interpreter.parser.parse_print_statement()
    interpreter.scope_manager.current_scope.add_symbol('a', DecimalVariable('a', 5))
    interpreter.scope_manager.current_scope.add_symbol('b', DecimalVariable('b', 3))
    interpreter.visit_print_statement(print_statement)
    assert interpreter.scope_manager.last_result == 'result: 4.0 is correct. 2'


def test_init_statement():
    interpreter = create_interpreter('dec a = 5;')
    init_statement = interpreter.parser.parse_init_statement()
    interpreter.visit_init_statement(init_statement)
    assert len(interpreter.scope_manager.current_scope.symbols) == 1
    variable = interpreter.scope_manager.current_scope.symbols['a']
    assert isinstance(variable, DecimalVariable)
    assert variable.name == 'a'
    assert variable.value == 5


def test_init_statement2():
    interpreter = create_interpreter('cur a = 5 eur;')
    init_statement = interpreter.parser.parse_init_statement()
    interpreter.visit_init_statement(init_statement)
    assert len(interpreter.scope_manager.current_scope.symbols) == 1
    variable = interpreter.scope_manager.current_scope.symbols['a']
    assert isinstance(variable, CurrencyVariable)
    assert variable.name == 'a'
    assert variable.value == 5
    assert variable.currency == 'eur'


def test_init_statement3():
    interpreter = create_interpreter('cur a = 5;')
    init_statement = interpreter.parser.parse_init_statement()
    with pytest.raises(CurrencyNotDefinedError):
        interpreter.visit_init_statement(init_statement)


def test_init_statement4():
    interpreter = create_interpreter('void a = 5;')
    init_statement = interpreter.parser.parse_init_statement()
    with pytest.raises(InvalidVariableTypeError):
        interpreter.visit_init_statement(init_statement)


def test_init_statement5():
    interpreter = create_interpreter('dec a;')
    init_statement = interpreter.parser.parse_init_statement()
    interpreter.visit_init_statement(init_statement)
    assert len(interpreter.scope_manager.current_scope.symbols) == 1
    variable = interpreter.scope_manager.current_scope.symbols['a']
    assert isinstance(variable, DecimalVariable)
    assert variable.name == 'a'
    assert variable.value is None


def test_init_statement6():
    interpreter = create_interpreter('cur a;')
    init_statement = interpreter.parser.parse_init_statement()
    interpreter.visit_init_statement(init_statement)
    assert len(interpreter.scope_manager.current_scope.symbols) == 1
    variable = interpreter.scope_manager.current_scope.symbols['a']
    assert isinstance(variable, CurrencyVariable)
    assert variable.name == 'a'
    assert variable.value is None
    assert variable.currency is None


def test_init_statement8():
    interpreter = create_interpreter('dec a = 5 eur;')
    init_statement = interpreter.parser.parse_init_statement()
    with pytest.raises(CurrencyUsedForDecimalVariableError):
        interpreter.visit_init_statement(init_statement)


def test_init_statement9():  # overwrite
    interpreter = create_interpreter('dec a = 5;')
    interpreter.scope_manager.current_scope.add_symbol('a', DecimalVariable('a', 5))
    init_statement = interpreter.parser.parse_init_statement()
    with pytest.raises(OverwriteError):
        interpreter.visit_init_statement(init_statement)


def test_init_statement10():
    interpreter = create_interpreter('dec a = -b;')
    interpreter.scope_manager.current_scope.add_symbol('b', DecimalVariable('b', 5))
    init_statement = interpreter.parser.parse_init_statement()
    interpreter.visit_init_statement(init_statement)
    assert len(interpreter.scope_manager.current_scope.symbols) == 2
    variable = interpreter.scope_manager.current_scope.symbols['b']
    assert isinstance(variable, DecimalVariable)
    assert variable.name == 'b'
    assert variable.value == 5
    variable = interpreter.scope_manager.current_scope.symbols['a']
    assert isinstance(variable, DecimalVariable)
    assert variable.name == 'a'
    assert variable.value == -5


def test_init_statement11():
    interpreter = create_interpreter('dec a = -5;')
    interpreter.scope_manager.current_scope.add_symbol('b', DecimalVariable('b', 5))
    init_statement = interpreter.parser.parse_init_statement()
    interpreter.visit_init_statement(init_statement)
    variable = interpreter.scope_manager.current_scope.symbols['a']
    assert isinstance(variable, DecimalVariable)
    assert variable.name == 'a'
    assert variable.value == -5


def test_init_statement12():
    interpreter = create_interpreter('cur a = -b;')
    interpreter.scope_manager.current_scope.add_symbol('b', CurrencyVariable('b', 5, 'eur'))
    init_statement = interpreter.parser.parse_init_statement()
    interpreter.visit_init_statement(init_statement)
    assert len(interpreter.scope_manager.current_scope.symbols) == 2
    variable = interpreter.scope_manager.current_scope.symbols['b']
    assert isinstance(variable, CurrencyVariable)
    assert variable.name == 'b'
    assert variable.value == 5
    assert variable.currency == 'eur'
    variable = interpreter.scope_manager.current_scope.symbols['a']
    assert isinstance(variable, CurrencyVariable)
    assert variable.name == 'a'
    assert variable.value == -5
    assert variable.currency == 'eur'


def test_init_statement13():
    interpreter = create_interpreter('cur a = -5 eur;')
    init_statement = interpreter.parser.parse_init_statement()
    interpreter.visit_init_statement(init_statement)
    assert len(interpreter.scope_manager.current_scope.symbols) == 1
    variable = interpreter.scope_manager.current_scope.symbols['a']
    assert isinstance(variable, CurrencyVariable)
    assert variable.name == 'a'
    assert variable.value == -5
    assert variable.currency == 'eur'


def test_init_statement14():
    interpreter = create_interpreter('dec result = - (a + b);')
    interpreter.scope_manager.current_scope.add_symbol('a', DecimalVariable('a', 5))
    interpreter.scope_manager.current_scope.add_symbol('b', DecimalVariable('b', 3))
    init_statement = interpreter.parser.parse_init_statement()
    interpreter.visit_init_statement(init_statement)
    variable = interpreter.scope_manager.current_scope.symbols['result']
    assert isinstance(variable, DecimalVariable)
    assert variable.name == 'result'
    assert variable.value == -8


def test_assign_statement():  # with 'a' already declared
    interpreter = create_interpreter('a = 5;')
    interpreter.scope_manager.current_scope.add_symbol('a', DecimalVariable('a', 10))
    assert len(interpreter.scope_manager.current_scope.symbols) == 1
    variable = interpreter.scope_manager.current_scope.symbols['a']
    assert isinstance(variable, DecimalVariable)
    assert variable.name == 'a'
    assert variable.value == 10
    assign_statement = interpreter.parser.parse_assign_statement_or_function_call()
    interpreter.visit_assign_statement(assign_statement)
    variable = interpreter.scope_manager.current_scope.symbols['a']
    assert variable.name == 'a'
    assert variable.value == 5


def test_assign_statement2():  # with 'a' not declared before
    interpreter = create_interpreter('a = 5;')
    assign_statement = interpreter.parser.parse_assign_statement_or_function_call()
    with pytest.raises(VariableNotDeclaredError):
        interpreter.visit_assign_statement(assign_statement)


def test_assign_statement3():  # with 'a' already declared
    interpreter = create_interpreter('a = 5 pln;')
    interpreter.scope_manager.current_scope.add_symbol('a', CurrencyVariable('a', 10, 'eur'))
    assert len(interpreter.scope_manager.current_scope.symbols) == 1
    variable = interpreter.scope_manager.current_scope.symbols['a']
    assert isinstance(variable, CurrencyVariable)
    assert variable.name == 'a'
    assert variable.value == 10
    assert variable.currency == 'eur'
    assign_statement = interpreter.parser.parse_assign_statement_or_function_call()
    interpreter.visit_assign_statement(assign_statement)
    variable = interpreter.scope_manager.current_scope.symbols['a']
    assert variable.name == 'a'
    assert variable.value == 5
    assert variable.currency == 'pln'


def test_assign_statement4():  # with 'a' not declared before
    interpreter = create_interpreter('a = 5 eur;')
    assign_statement = interpreter.parser.parse_assign_statement_or_function_call()
    with pytest.raises(VariableNotDeclaredError):
        interpreter.visit_assign_statement(assign_statement)


def test_assign_statement5():  # cur a; a = 5 pln;
    interpreter = create_interpreter('a = 5 pln;')
    interpreter.scope_manager.current_scope.add_symbol('a', CurrencyVariable('a'))
    assert len(interpreter.scope_manager.current_scope.symbols) == 1
    variable = interpreter.scope_manager.current_scope.symbols['a']
    assert isinstance(variable, CurrencyVariable)
    assert variable.name == 'a'
    assert variable.value is None
    assert variable.currency is None
    assign_statement = interpreter.parser.parse_assign_statement_or_function_call()
    interpreter.visit_assign_statement(assign_statement)
    variable = interpreter.scope_manager.current_scope.symbols['a']
    assert isinstance(variable, CurrencyVariable)
    assert variable.name == 'a'
    assert variable.value == 5
    assert variable.currency == 'pln'


def test_assign_statement6():  # cur a; a = 5;
    interpreter = create_interpreter('a = 5;')
    interpreter.scope_manager.current_scope.add_symbol('a', CurrencyVariable('a'))
    assert len(interpreter.scope_manager.current_scope.symbols) == 1
    variable = interpreter.scope_manager.current_scope.symbols['a']
    assert isinstance(variable, CurrencyVariable)
    assert variable.name == 'a'
    assert variable.value is None
    assert variable.currency is None
    assign_statement = interpreter.parser.parse_assign_statement_or_function_call()
    with pytest.raises(CurrencyNotDefinedOrChangeVariableTypeError):
        interpreter.visit_assign_statement(assign_statement)


def test_assign_statement7():  # dec a = 5; a = 10 eur;
    interpreter = create_interpreter('a = 10 eur;')
    interpreter.scope_manager.current_scope.add_symbol('a', DecimalVariable('a', 5))
    assert len(interpreter.scope_manager.current_scope.symbols) == 1
    variable = interpreter.scope_manager.current_scope.symbols['a']
    assert isinstance(variable, DecimalVariable)
    assert variable.name == 'a'
    assert variable.value == 5
    assign_statement = interpreter.parser.parse_assign_statement_or_function_call()
    with pytest.raises(ChangeVariableTypeError):
        interpreter.visit_assign_statement(assign_statement)


def test_assign_statement8():  # a = 5 without type declared before
    interpreter = create_interpreter('a = 10 eur;')
    assign_statement = interpreter.parser.parse_assign_statement_or_function_call()
    with pytest.raises(VariableNotDeclaredError):
        interpreter.visit_assign_statement(assign_statement)


def test_assign_statement9():  # cur a = 5 eur; a = 10;
    interpreter = create_interpreter('a = 10;')
    interpreter.scope_manager.current_scope.add_symbol('a', CurrencyVariable('a', 5, 'eur'))
    assert len(interpreter.scope_manager.current_scope.symbols) == 1
    variable = interpreter.scope_manager.current_scope.symbols['a']
    assert isinstance(variable, CurrencyVariable)
    assert variable.name == 'a'
    assert variable.value == 5
    assert variable.currency == 'eur'
    assign_statement = interpreter.parser.parse_assign_statement_or_function_call()
    with pytest.raises(ChangeVariableTypeError):
        interpreter.visit_assign_statement(assign_statement)


def test_assign_statement10():  # dec a; a = b + c;
    interpreter = create_interpreter('a = b + c;')
    interpreter.scope_manager.current_scope.add_symbol('a', DecimalVariable('a', 5))
    interpreter.scope_manager.current_scope.add_symbol('b', DecimalVariable('a', 1))
    interpreter.scope_manager.current_scope.add_symbol('c', DecimalVariable('a', 100))
    assert len(interpreter.scope_manager.current_scope.symbols) == 3
    variable = interpreter.scope_manager.current_scope.symbols['a']
    assert isinstance(variable, DecimalVariable)
    assert variable.name == 'a'
    assert variable.value == 5
    assign_statement = interpreter.parser.parse_assign_statement_or_function_call()
    interpreter.visit_assign_statement(assign_statement)
    variable = interpreter.scope_manager.current_scope.symbols['a']
    assert isinstance(variable, DecimalVariable)
    assert variable.name == 'a'
    assert variable.value == 101


def test_assign_statement11():
    interpreter = create_interpreter('a = b;')
    interpreter.scope_manager.current_scope.add_symbol('a', DecimalVariable('a', 5))
    interpreter.scope_manager.current_scope.add_symbol('b', DecimalVariable('b', 10))
    assert len(interpreter.scope_manager.current_scope.symbols) == 2
    variable = interpreter.scope_manager.current_scope.symbols['a']
    assert isinstance(variable, DecimalVariable)
    assert variable.name == 'a'
    assert variable.value == 5
    variable = interpreter.scope_manager.current_scope.symbols['b']
    assert isinstance(variable, DecimalVariable)
    assert variable.name == 'b'
    assert variable.value == 10
    assign_statement = interpreter.parser.parse_assign_statement_or_function_call()
    interpreter.visit_assign_statement(assign_statement)
    variable = interpreter.scope_manager.current_scope.symbols['a']
    assert isinstance(variable, DecimalVariable)
    assert variable.name == 'a'
    assert variable.value == 10


def test_assign_statement12():
    interpreter = create_interpreter('a = b;')
    interpreter.scope_manager.current_scope.add_symbol('a', CurrencyVariable('a', 5, 'pln'))
    interpreter.scope_manager.current_scope.add_symbol('b', CurrencyVariable('b', 10, 'eur'))
    assert len(interpreter.scope_manager.current_scope.symbols) == 2
    variable = interpreter.scope_manager.current_scope.symbols['a']
    assert isinstance(variable, CurrencyVariable)
    assert variable.name == 'a'
    assert variable.value == 5
    assert variable.currency == 'pln'
    variable = interpreter.scope_manager.current_scope.symbols['b']
    assert isinstance(variable, CurrencyVariable)
    assert variable.name == 'b'
    assert variable.value == 10
    assert variable.currency == 'eur'
    assign_statement = interpreter.parser.parse_assign_statement_or_function_call()
    interpreter.visit_assign_statement(assign_statement)
    variable = interpreter.scope_manager.current_scope.symbols['a']
    assert isinstance(variable, CurrencyVariable)
    assert variable.name == 'a'
    assert variable.value == 10
    assert variable.currency == 'eur'


def test_assign_statement13():
    interpreter = create_interpreter('a = b;')
    interpreter.scope_manager.current_scope.add_symbol('a', DecimalVariable('a', 5))
    interpreter.scope_manager.current_scope.add_symbol('b', CurrencyVariable('b', 10, 'eur'))
    assert len(interpreter.scope_manager.current_scope.symbols) == 2
    variable = interpreter.scope_manager.current_scope.symbols['a']
    assert isinstance(variable, DecimalVariable)
    assert variable.name == 'a'
    assert variable.value == 5
    variable = interpreter.scope_manager.current_scope.symbols['b']
    assert isinstance(variable, CurrencyVariable)
    assert variable.name == 'b'
    assert variable.value == 10
    assert variable.currency == 'eur'
    assign_statement = interpreter.parser.parse_assign_statement_or_function_call()
    with pytest.raises(ChangeVariableTypeError):
        interpreter.visit_assign_statement(assign_statement)


def test_if_statement():
    interpreter = create_interpreter(' if (a > b) {'
                                     'b = 100;'
                                     '}')
    interpreter.scope_manager.current_scope.add_symbol('a', DecimalVariable('a', 5))
    interpreter.scope_manager.current_scope.add_symbol('b', DecimalVariable('b', 1))
    if_statement = interpreter.parser.parse_if_statement()
    interpreter.visit_if_statement(if_statement)
    assert interpreter.scope_manager.current_scope.symbols['b'].value == 100


def test_while_statement():
    interpreter = create_interpreter(' while (a < 3) {'
                                     'b = b + 5;'
                                     'a = a + 1;'
                                     '}')
    interpreter.scope_manager.current_scope.add_symbol('a', DecimalVariable('a', 0))
    interpreter.scope_manager.current_scope.add_symbol('b', DecimalVariable('b', 0))
    while_statement = interpreter.parser.parse_while_statement()
    interpreter.visit_while_statement(while_statement)
    assert interpreter.scope_manager.current_scope.symbols['b'].value == 15
    assert interpreter.scope_manager.current_scope.symbols['a'].value == 3


def test_function_def():  # signature, “(”, parameters, “)”, “{“, block, “}” ;
    interpreter = create_interpreter('void calculate(dec a, dec b) {'
                                     ' dec result = a + b;'
                                     '}')
    function_def = interpreter.parser.parse_function_def()
    interpreter.visit_function_def(function_def)
    assert len(interpreter.scope_manager.global_scope.symbols) == 1
    assert len(interpreter.scope_manager.global_scope.symbols['calculate'].parameters.signatures) == 2
    assert len(interpreter.scope_manager.global_scope.symbols['calculate'].block.statements) == 1


def test_return_statement():  # signature, “(”, parameters, “)”, “{“, block, “}” ;
    interpreter = create_interpreter('return a + b;')
    interpreter.scope_manager.current_scope.add_symbol('a', DecimalVariable('a', 3))
    interpreter.scope_manager.current_scope.add_symbol('b', DecimalVariable('b', 5))
    return_statement = interpreter.parser.parse_return_statement()
    interpreter.visit_return_statement(return_statement)
    assert isinstance(interpreter.scope_manager.last_result, DecimalVariable)
    assert interpreter.scope_manager.last_result.value == 8


def test_return_statement2():  # signature, “(”, parameters, “)”, “{“, block, “}” ;
    interpreter = create_interpreter('return result;')
    interpreter.scope_manager.current_scope.add_symbol('result', DecimalVariable('result', 3))
    return_statement = interpreter.parser.parse_return_statement()
    interpreter.visit_return_statement(return_statement)
    assert isinstance(interpreter.scope_manager.last_result, DecimalVariable)
    assert interpreter.scope_manager.last_result.value == 3


def test_return_statement3():  # signature, “(”, parameters, “)”, “{“, block, “}” ;
    interpreter = create_interpreter('return -result;')
    interpreter.scope_manager.current_scope.add_symbol('result', DecimalVariable('result', 3))
    return_statement = interpreter.parser.parse_return_statement()
    interpreter.visit_return_statement(return_statement)
    assert interpreter.scope_manager.current_scope.symbols['result'].value == 3
    assert isinstance(interpreter.scope_manager.last_result, DecimalVariable)
    assert interpreter.scope_manager.last_result.value == -3


def test_program():
    interpreter = create_interpreter('dec add(dec a, dec b) {'
                                     'return a + b;'
                                     '}'
                                     ''
                                     'void main() {'
                                     'dec result = add(1, 2);'
                                     '}')
    interpreter.interpret()
    assert len(interpreter.scope_manager.global_scope.symbols) == 2
    assert len(interpreter.scope_manager.current_scope.symbols) == 1
    result = interpreter.scope_manager.current_scope.symbols['result']
    assert isinstance(result, DecimalVariable)
    assert result.name == 'result'
    assert result.value == 3


def test_program2():
    interpreter = create_interpreter('dec add(dec a, dec b) {'
                                     'return a + b;'
                                     '}'
                                     ''
                                     'void main() {'
                                     'dec b = 1;'
                                     'dec c = 2;'
                                     'dec a = add(b, c);'
                                     '}')
    interpreter.interpret()
    assert len(interpreter.scope_manager.global_scope.symbols) == 2
    assert len(interpreter.scope_manager.current_scope.symbols) == 3
    result = interpreter.scope_manager.current_scope.symbols['a']
    assert isinstance(result, DecimalVariable)
    assert result.name == 'a'
    assert result.value == 3


def test_program3():
    interpreter = create_interpreter('dec multiply(dec a, dec b) {'
                                     'return a * b;'
                                     '}'
                                     ''
                                     'dec add(dec a, dec b) {'
                                     'dec result = multiply(5, 6);'
                                     'return a + b + result;'
                                     '}'
                                     ''
                                     'void main() {'
                                     'dec b = 1;'
                                     'dec c = 2;'
                                     'dec a = add(b, c);'
                                     '}')
    interpreter.interpret()
    assert len(interpreter.scope_manager.global_scope.symbols) == 3
    assert len(interpreter.scope_manager.current_scope.symbols) == 3
    result = interpreter.scope_manager.current_scope.symbols['a']
    assert isinstance(result, DecimalVariable)
    assert result.name == 'a'
    assert result.value == 33


def test_program4():
    interpreter = create_interpreter('dec add() {'
                                     'cur a = 5 eur;'
                                     'return a;'
                                     '}'
                                     ''
                                     'void main() {'
                                     'add();'
                                     '}')
    with pytest.raises(InvalidReturnedTypeError):
        interpreter.interpret()


def test_program5():
    interpreter = create_interpreter('dec add(dec a, dec b) {'
                                     'return a + b;'
                                     '}'
                                     ''
                                     'void main() {'
                                     'add(1);'
                                     '}')
    with pytest.raises(IncorrectArgumentsNumberError):
        interpreter.interpret()


def test_program6():
    interpreter = create_interpreter('dec add(dec a, dec b) {'
                                     'return a + b;'
                                     '}'
                                     ''
                                     'void main() {'
                                     'cur x = 5 eur;'
                                     'dec y = 10;'
                                     'add(x, y);'
                                     '}')
    with pytest.raises(InvalidArgumentTypeError):
        interpreter.interpret()


def test_program7():
    interpreter = create_interpreter('dec add(dec a, dec b) {'
                                     'return a + b;'
                                     '}')
    with pytest.raises(MainNotDeclaredError):
        interpreter.interpret()


def test_program8():
    interpreter = create_interpreter('void main() {'
                                     'ggg a = 5;'
                                     '}')
    with pytest.raises(SyntaxxError):
        interpreter.interpret()


def test_program9():
    interpreter = create_interpreter('dec add(dec a, dec b) {'
                                     'return a + b;'
                                     '}'
                                     ''
                                     'void main() {'
                                     'dec result = -add(1, 2);'
                                     '}')
    interpreter.interpret()
    assert len(interpreter.scope_manager.global_scope.symbols) == 2
    assert len(interpreter.scope_manager.current_scope.symbols) == 1
    result = interpreter.scope_manager.current_scope.symbols['result']
    assert isinstance(result, DecimalVariable)
    assert result.name == 'result'
    assert result.value == -3


def test_exchange():
    Currencies.currencies = {
        "pln": {
            "chf": 1,
            "gbd": 50
        },
        "chf": {
            "pln": 1,
            "gbd": 1
        },
        "gbd": {
            "pln": 1,
            "chf": 1
        }
    }
    var = CurrencyVariable('var', 10, 'pln')
    var.exchange('gbd')
    assert var.value == 500
    assert var.currency == 'gbd'


def test_currency_calculations():
    interpreter = create_interpreter('cur result = a + b;')
    set_currencies()
    interpreter.scope_manager.current_scope.add_symbol('a', CurrencyVariable('a', 5, 'pln'))
    interpreter.scope_manager.current_scope.add_symbol('b', CurrencyVariable('b', 10, 'eur'))
    init_statement = interpreter.parser.parse_init_statement()
    interpreter.visit_init_statement(init_statement)
    result = interpreter.scope_manager.current_scope.symbols['result']
    assert isinstance(result, CurrencyVariable)
    assert result.currency == 'pln'
    assert result.value == 175


def test_currency_calculations2():
    interpreter = create_interpreter('cur result = a - b;')
    set_currencies()
    interpreter.scope_manager.current_scope.add_symbol('a', CurrencyVariable('a', 5, 'pln'))
    interpreter.scope_manager.current_scope.add_symbol('b', CurrencyVariable('b', 10, 'eur'))
    init_statement = interpreter.parser.parse_init_statement()
    interpreter.visit_init_statement(init_statement)
    result = interpreter.scope_manager.current_scope.symbols['result']
    assert isinstance(result, CurrencyVariable)
    assert result.currency == 'pln'
    assert result.value == -165


def test_currency_calculations3():
    interpreter = create_interpreter('cur result = a + b chf;')
    set_currencies()
    interpreter.scope_manager.current_scope.add_symbol('a', CurrencyVariable('a', 5, 'pln'))
    interpreter.scope_manager.current_scope.add_symbol('b', CurrencyVariable('b', 10, 'eur'))
    init_statement = interpreter.parser.parse_init_statement()
    interpreter.visit_init_statement(init_statement)
    result = interpreter.scope_manager.current_scope.symbols['result']
    assert isinstance(result, CurrencyVariable)
    assert result.currency == 'pln'
    assert result.value == 905


def test_currency_calculations4():
    interpreter = create_interpreter('cur result = gbd a + b;')
    set_currencies()
    interpreter.scope_manager.current_scope.add_symbol('a', CurrencyVariable('a', 5, 'pln'))
    interpreter.scope_manager.current_scope.add_symbol('b', CurrencyVariable('b', 10, 'eur'))
    init_statement = interpreter.parser.parse_init_statement()
    interpreter.visit_init_statement(init_statement)
    result = interpreter.scope_manager.current_scope.symbols['result']
    assert isinstance(result, CurrencyVariable)
    assert result.currency == 'gbd'
    assert result.value == 200


def test_currency_calculations5():
    interpreter = create_interpreter('cur result = a gbd + b;')
    set_currencies()
    interpreter.scope_manager.current_scope.add_symbol('a', CurrencyVariable('a', 5, 'pln'))
    interpreter.scope_manager.current_scope.add_symbol('b', CurrencyVariable('b', 10, 'eur'))
    init_statement = interpreter.parser.parse_init_statement()
    interpreter.visit_init_statement(init_statement)
    result = interpreter.scope_manager.current_scope.symbols['result']
    assert isinstance(result, CurrencyVariable)
    assert result.currency == 'gbd'
    assert result.value == 200


def test_currency_calculations6():
    interpreter = create_interpreter('cur result = a + chf b gbd;')
    set_currencies()
    interpreter.scope_manager.current_scope.add_symbol('a', CurrencyVariable('a', 5, 'pln'))
    interpreter.scope_manager.current_scope.add_symbol('b', CurrencyVariable('b', 10, 'eur'))
    init_statement = interpreter.parser.parse_init_statement()
    interpreter.visit_init_statement(init_statement)
    result = interpreter.scope_manager.current_scope.symbols['result']
    assert isinstance(result, CurrencyVariable)
    assert result.currency == 'pln'
    assert result.value == 9725


def test_currency_calculations7():
    interpreter = create_interpreter('cur result = gbd (a + b);')
    set_currencies()
    interpreter.scope_manager.current_scope.add_symbol('a', CurrencyVariable('a', 5, 'pln'))
    interpreter.scope_manager.current_scope.add_symbol('b', CurrencyVariable('b', 10, 'eur'))
    init_statement = interpreter.parser.parse_init_statement()
    interpreter.visit_init_statement(init_statement)
    result = interpreter.scope_manager.current_scope.symbols['result']
    assert isinstance(result, CurrencyVariable)
    assert result.currency == 'gbd'
    assert result.value == 350


def test_currency_calculations8():
    interpreter = create_interpreter('cur result = gbd (a + b) pln;')
    set_currencies()
    interpreter.scope_manager.current_scope.add_symbol('a', CurrencyVariable('a', 5, 'pln'))
    interpreter.scope_manager.current_scope.add_symbol('b', CurrencyVariable('b', 10, 'eur'))
    init_statement = interpreter.parser.parse_init_statement()
    interpreter.visit_init_statement(init_statement)
    result = interpreter.scope_manager.current_scope.symbols['result']
    assert isinstance(result, CurrencyVariable)
    assert result.currency == 'pln'
    assert result.value == 3150


def test_currency_calculations9():
    interpreter = create_interpreter('cur result = gbd (eur a + b) chf;')
    set_currencies()
    interpreter.scope_manager.current_scope.add_symbol('a', CurrencyVariable('a', 5, 'pln'))
    interpreter.scope_manager.current_scope.add_symbol('b', CurrencyVariable('b', 10, 'usd'))
    init_statement = interpreter.parser.parse_init_statement()
    interpreter.visit_init_statement(init_statement)
    result = interpreter.scope_manager.current_scope.symbols['result']
    assert isinstance(result, CurrencyVariable)
    assert result.currency == 'chf'
    assert result.value == 34200


def test_currency_calculations10():
    interpreter = create_interpreter('cur result = pln a pln;')
    set_currencies()
    interpreter.scope_manager.current_scope.add_symbol('a', CurrencyVariable('a', 5, 'pln'))
    init_statement = interpreter.parser.parse_init_statement()
    interpreter.visit_init_statement(init_statement)
    result = interpreter.scope_manager.current_scope.symbols['result']
    assert isinstance(result, CurrencyVariable)
    assert result.currency == 'pln'
    assert result.value == 5


def test_currency_calculations11():
    interpreter = create_interpreter('cur result = pln (a + b) pln;')
    set_currencies()
    interpreter.scope_manager.current_scope.add_symbol('a', CurrencyVariable('a', 5, 'pln'))
    interpreter.scope_manager.current_scope.add_symbol('b', CurrencyVariable('b', 10, 'pln'))
    init_statement = interpreter.parser.parse_init_statement()
    interpreter.visit_init_statement(init_statement)
    result = interpreter.scope_manager.current_scope.symbols['result']
    assert isinstance(result, CurrencyVariable)
    assert result.currency == 'pln'
    assert result.value == 15


def test_currency_calculations12():
    interpreter = create_interpreter('cur result = a b.get_currency();')
    set_currencies()
    interpreter.scope_manager.current_scope.add_symbol('a', CurrencyVariable('a', 5, 'pln'))
    interpreter.scope_manager.current_scope.add_symbol('b', CurrencyVariable('b', 10, 'eur'))
    init_statement = interpreter.parser.parse_init_statement()
    interpreter.visit_init_statement(init_statement)
    result = interpreter.scope_manager.current_scope.symbols['result']
    assert isinstance(result, CurrencyVariable)
    assert result.currency == 'eur'
    assert result.value == 20

