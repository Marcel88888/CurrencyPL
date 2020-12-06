import sys
import io
import pytest
from ..src.lexer.lexer import Lexer
from ..src.lexer.token import Token, TokenTypes
from ..src.lexer.tokens import Tokens
from ..src.source.source import FileSource
from ..src.exceptions.exceptions import *


def create_lexer(source_string):
    return Lexer(FileSource(io.StringIO(source_string)))


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

    lexer.get_next_token()
    assert lexer.token.type == TokenTypes.EOT
    assert lexer.token.value is None


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

    lexer.get_next_token()
    assert lexer.token.type == TokenTypes.EOT
    assert lexer.token.value is None


# KEYWORDS

def test_keyword_if():
    lexer = create_lexer("if")

    lexer.get_next_token()
    assert lexer.token.type == TokenTypes.IF














# def test_keywords():
#     keywords = list(Tokens.keywords.keys())
#     keywords_token_types = list(Tokens.keywords.values())
#     for index, keyword in enumerate(keywords):
#         lexer = create_lexer(keyword)
#         lexer.get_next_token()
#         assert lexer.token.type == keywords_token_types[index]
#
#
# def test_single_operators():
#     single_operators = list(Tokens.single_operators.keys())
#     single_operators_token_types = list(Tokens.single_operators.values())
#     for index, single_operator in enumerate(single_operators):
#         lexer = create_lexer(single_operator)
#         lexer.get_next_token()
#         assert lexer.token.type == single_operators_token_types[index]
#
#
# def test_double_operators():
#     double_operators = list(Tokens.double_operators.keys())
#     double_operators_token_types = list(Tokens.double_operators.values())
#     for index, double_operator in enumerate(double_operators):
#         lexer = create_lexer(double_operator)
#         lexer.get_next_token()
#         assert lexer.token.type == double_operators_token_types[index]


