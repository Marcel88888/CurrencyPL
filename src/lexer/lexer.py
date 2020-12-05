from typing import Final
from .token import Token
from .tokens import Tokens
from .token_types import TokenTypes
from ..exceptions.exceptions import InvalidTokenError


class Lexer:
    def __init__(self, source, currencies):
        self.source = source
        self.currencies = currencies
        self.char = None
        self.token = None
        self.TOKEN_MAX_LENGTH: Final = 50

    def get_next_token(self):
        self.skip_spaces()
        self.char = self.source.get_next_char()
        self.token = Token(self.source.line_number, self.source.line_number)
        self.parse_token()

    def parse_token(self):
        if self.is_eof():
            self.token.type = TokenTypes.EOT
        elif self.char.isalpha():
            self.parse_keyword_or_identifier()
            return
        elif self.char.isdigit():
            self.parse_number()
        elif self.char == TokenTypes.QUOTATION_MARK:
            self.parse_string()
        elif self.try_to_parse_single_operator():
            return
        elif self.try_to_parse_double_operator():
            return
        else:
            raise InvalidTokenError(self.source.get_position())

    def parse_string(self):
        pass

    def parse_keyword_or_identifier(self):
        kw_or_id = self.read_keyword_or_identifier()
        if kw_or_id in Tokens.keywords:
            # keyword
            self.token = Token(self.source.line, self.source.column, kw_or_id, Tokens.keywords[kw_or_id])
        else:
            # identifier
            self.token = Token(self.source.line, self.source.column, kw_or_id, TokenTypes.IDENTIFIER)

    def read_keyword_or_identifier(self):
        kw_or_id = ""
        while self.char.isalpha or self.char.isdigit or self.char == '_':
            kw_or_id += self.char
            self.char = self.source.get_next_char()
        return kw_or_id


    def parse_number(self):
        pass

    def try_to_parse_single_operator(self):
        pass

    def try_to_parse_double_operator(self):
        pass

    def skip_spaces(self):
        while self.char.isspace():
            self.source.get_next_char()

    def is_eof(self):
        return self.char == ''




