import io
import pytest
from ..src.lexer.lexer import Lexer
from ..src.lexer.token import TokenTypes
from ..src.lexer.tokens import Tokens
from ..src.source.currencies_reader import CurrenciesReader
from ..src.source.source import FileSource
from ..src.parser.parser import Parser
from ..src.exceptions.exceptions import _SyntaxError


def create_parser(source_string):
    currencies_reader = CurrenciesReader("resources/currencies.json")
    currencies = currencies_reader.currencies
    for currency in currencies:
        Tokens.keywords[currency.name] = TokenTypes.CURRENCY_TYPE
    lexer = Lexer(FileSource(io.StringIO(source_string)))
    return Parser(lexer)


def test_signature():
    parser = create_parser("dec var")
    signature = parser.parse_signature()
    assert signature.type == TokenTypes.DECIMAL
    assert signature.id == 'var'


def test_signature_without_type():
    parser = create_parser("var")
    assert parser.parse_signature() is None


def test_parameters():
    parser = create_parser("dec a, cur b, dec var")
    parameters = parser.parse_parameters()

    assert parameters.signatures[0].type == TokenTypes.DECIMAL
    assert parameters.signatures[0].id == 'a'

    assert parameters.signatures[1].type == TokenTypes.CURRENCY
    assert parameters.signatures[1].id == 'b'

    assert parameters.signatures[2].type == TokenTypes.DECIMAL
    assert parameters.signatures[2].id == 'var'


def test_incorrect_parameters():
    parser = create_parser("dec a, b")
    with pytest.raises(_SyntaxError):
        parser.parse_parameters()


def test_get_currency():
    parser = create_parser("var.get_currency()")
    assert parser.parse_get_currency().id == 'var'


def test_incorrect_get_currency():
    parser = create_parser("var.get_currency(")
    assert parser.parse_get_currency() is None


def test_incorrect_get_currency2():
    parser = create_parser("var,get_currency(")
    assert parser.parse_get_currency() is None


def test_relational_cond():  # primaryCond, [ relationOp, primaryCond ];
    parser = create_parser("a > b")
    relational_cond = parser.parse_relational_cond()
    assert relational_cond.primary_conds[0].expression.multipl_exprs[0].primary_exprs[0].id == 'a'
    assert relational_cond.relation_op == TokenTypes.GREATER_THAN
    assert relational_cond.primary_conds[1].expression.multipl_exprs[0].primary_exprs[0].id == 'b'

