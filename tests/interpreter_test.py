from ..src.source.currencies_reader import CurrenciesReader
from ..src.lexer.tokens import Tokens
from ..src.source.source import FileSource
from ..src.lexer.lexer import Lexer
from ..src.parser import parser as p
from ..src.parser.grammar import *
from ..src.interpreter.scope import *
import io


def create_interpreter():
    currencies_reader = CurrenciesReader("resources/currencies.json")
    currencies = currencies_reader.currencies
    for currency in currencies:
        Tokens.keywords[currency.name] = TokenTypes.CURRENCY_TYPE
    lexer = Lexer(FileSource(io.StringIO("")))
    parser = p.Parser(lexer)
    return Interpreter(parser)


def test_visit_get_currency():
    interpreter = create_interpreter()
    interpreter.scope_manager.current_scope.add_symbol('var', CurrencyVariable('var', 10, Currency('eur', 1.45)))
    get_currency = GetCurrency('var')
    interpreter.visit_get_currency(get_currency)
    assert interpreter.scope_manager.last_result is not None
    assert isinstance(interpreter.scope_manager.last_result, Currency)
    assert interpreter.scope_manager.last_result.name == 'eur'
    assert interpreter.scope_manager.last_result.rate == 1.45
