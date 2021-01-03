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


def test_primary_expr():  # def __init__(self, minus=False, currency1=None, get_currency1=None, number=None,
    # _id=None, parenth_expr=None, function_call=None, currency2=None, get_currency2=None):
    parser = create_parser("a.get_currency() b")
    primary_expr = parser.parse_primary_expr()
    assert primary_expr is not None
    assert primary_expr.minus is False
    assert primary_expr.currency1 is None
    assert primary_expr.get_currency1.id == 'a'
    assert primary_expr.number is None
    assert primary_expr.id == 'b'
    assert primary_expr.parenth_expr is None
    assert primary_expr.function_call is None
    assert primary_expr.currency2 is None
    assert primary_expr.get_currency2 is None


def test_primary_expr2():  # def __init__(self, minus=False, currency1=None, get_currency1=None, number=None,
    # _id=None, parenth_expr=None, function_call=None, currency2=None, get_currency2=None):
    parser = create_parser("-b")
    primary_expr = parser.parse_primary_expr()
    assert primary_expr is not None
    assert primary_expr.minus is True
    assert primary_expr.currency1 is None
    assert primary_expr.get_currency1 is None
    assert primary_expr.number is None
    assert primary_expr.id == 'b'
    assert primary_expr.parenth_expr is None
    assert primary_expr.function_call is None
    assert primary_expr.currency2 is None
    assert primary_expr.get_currency2 is None


def test_primary_expr3():  # def __init__(self, minus=False, currency1=None, get_currency1=None, number=None,
    # _id=None, parenth_expr=None, function_call=None, currency2=None, get_currency2=None):
    parser = create_parser("b usd")
    primary_expr = parser.parse_primary_expr()
    assert primary_expr is not None
    assert primary_expr.minus is False
    assert primary_expr.currency1 is None
    assert primary_expr.get_currency1 is None
    assert primary_expr.number is None
    assert primary_expr.id == 'b'
    assert primary_expr.parenth_expr is None
    assert primary_expr.function_call is None
    assert primary_expr.currency2 == 'usd'
    assert primary_expr.get_currency2 is None


def test_primary_expr4():  # def __init__(self, minus=False, currency1=None, get_currency1=None, number=None,
    # _id=None, parenth_expr=None, function_call=None, currency2=None, get_currency2=None):
    parser = create_parser("a.get_currency() b usd")
    primary_expr = parser.parse_primary_expr()
    assert primary_expr is not None
    assert primary_expr.minus is False
    assert primary_expr.currency1 is None
    assert primary_expr.get_currency1.id == 'a'
    assert primary_expr.number is None
    assert primary_expr.id == 'b'
    assert primary_expr.parenth_expr is None
    assert primary_expr.function_call is None
    assert primary_expr.currency2 == 'usd'
    assert primary_expr.get_currency2 is None


def test_primary_expr5():  # def __init__(self, minus=False, currency1=None, get_currency1=None, number=None,
    # _id=None, parenth_expr=None, function_call=None, currency2=None, get_currency2=None):
    parser = create_parser("usd b a.get_currency()")
    primary_expr = parser.parse_primary_expr()
    assert primary_expr is not None
    assert primary_expr.minus is False
    assert primary_expr.currency1 == 'usd'
    assert primary_expr.get_currency1 is None
    assert primary_expr.number is None
    assert primary_expr.id == 'b'
    assert primary_expr.parenth_expr is None
    assert primary_expr.function_call is None
    assert primary_expr.currency2 is None
    assert primary_expr.get_currency2.id == 'a'


def test_primary_expr6():  # def __init__(self, minus=False, currency1=None, get_currency1=None, number=None,
    # _id=None, parenth_expr=None, function_call=None, currency2=None, get_currency2=None):
    parser = create_parser("usd 5.2 a.get_currency()")
    primary_expr = parser.parse_primary_expr()
    assert primary_expr is not None
    assert primary_expr.minus is False
    assert primary_expr.currency1 == 'usd'
    assert primary_expr.get_currency1 is None
    assert primary_expr.number == 5.2
    assert primary_expr.id is None
    assert primary_expr.parenth_expr is None
    assert primary_expr.function_call is None
    assert primary_expr.currency2 is None
    assert primary_expr.get_currency2.id == 'a'


def test_primary_expr7():  # def __init__(self, minus=False, currency1=None, get_currency1=None, number=None,
    # _id=None, parenth_expr=None, function_call=None, currency2=None, get_currency2=None):
    parser = create_parser("a.get_currency() 5.2 usd")
    primary_expr = parser.parse_primary_expr()
    assert primary_expr is not None
    assert primary_expr.minus is False
    assert primary_expr.currency1 is None
    assert primary_expr.get_currency1.id == 'a'
    assert primary_expr.number == 5.2
    assert primary_expr.id is None
    assert primary_expr.parenth_expr is None
    assert primary_expr.function_call is None
    assert primary_expr.currency2 == 'usd'
    assert primary_expr.get_currency2 is None


# def test_equality_cond():  # relationalCond, [ equalOp, relationalCond ] ;
#


def test_relational_cond():  # primaryCond, [ relationOp, primaryCond ];
    parser = create_parser("a > b")
    relational_cond = parser.parse_relational_cond()
    assert relational_cond.primary_conds[0].expression.multipl_exprs[0].primary_exprs[0].id == 'a'
    assert relational_cond.relation_op == TokenTypes.GREATER_THAN
    assert relational_cond.primary_conds[1].expression.multipl_exprs[0].primary_exprs[0].id == 'b'


def test_primary_cond():  # [ unaryOp ], ( parenthCond | expression ) ;
    parser = create_parser("! a + b")
    primary_cond = parser.parse_primary_cond()
    assert primary_cond.unary_op is True
    assert primary_cond.expression.multipl_exprs[0].primary_exprs[0].id == 'a'
    assert primary_cond.expression.additive_op == TokenTypes.PLUS
    assert primary_cond.expression.multipl_exprs[1].primary_exprs[0].id == 'b'


def test_multipl_expr():  # primaryExpr, { multiplOp, primaryExpr } ;
    parser = create_parser("a * 5")
    multipl_expr = parser.parse_multipl_expr()
    assert multipl_expr.primary_exprs[0].id == 'a'
    assert multipl_expr.multipl_op == TokenTypes.MULTIPLY
    assert multipl_expr.primary_exprs[1].number == 5


def test_expression():  # multiplExpr, { additiveOp, multiplExpr } ;
    parser = create_parser("a * b + c")
    expression = parser.parse_expression()
    assert expression.multipl_exprs[0].primary_exprs[0].id == 'a'
    assert expression.multipl_exprs[0].multipl_op == TokenTypes.MULTIPLY
    assert expression.multipl_exprs[0].primary_exprs[1].id == 'b'
    assert expression.additive_op == TokenTypes.PLUS
    assert expression.multipl_exprs[1].primary_exprs[0].id == 'c'


