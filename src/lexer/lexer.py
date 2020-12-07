from .token import Token
from .tokens import Tokens
from .token_types import TokenTypes
from ..exceptions.exceptions import *


class Lexer:
    def __init__(self, source, currencies=None):
        self.source = source
        self.currencies = currencies
        self.char = self.source.get_next_char()
        self.token = None
        self.line = None
        self.column = None
        self.TOKEN_MAX_LENGTH = 50
        self.STRING_MAX_LENGTH = 1000
        # TODO add currencies

    def get_next_token(self):
        # self.char = self.source.get_next_char()
        # print(self.char)
        self.skip_spaces()
        self.line = self.source.line
        self.column = self.source.column - 1
        print(self.char)
        self.build_token()

    def build_token(self):
        if self.is_eof():
            self.token = Token(TokenTypes.EOT, self.line, self.column)
        elif self.char.isalpha():
            self.build_keyword_or_identifier()
            # print(self.token.type)
            return
        elif self.char.isdigit():
            self.build_number()
            # print(self.token.type)
            return
        elif self.char == '"':
            self.build_string()
            # print(self.token.type)
            return
        elif self.char == '#':
            self.skip_comment()
        elif self.try_to_build_double_operator():
            # print(self.token.type)
            return
        elif self.try_to_build_single_operator():
            # print(self.token.type)
            print("AAAAAAAAAAAA")
            return
        else:
            raise InvalidTokenError(self.source.line, self.source.column)

    def build_keyword_or_identifier(self):
        kw_or_id = self.read_keyword_or_identifier()
        if kw_or_id in Tokens.keywords:
            # keyword
            self.token = Token(Tokens.keywords[kw_or_id], self.line, self.column, kw_or_id, )
        else:
            # identifier
            self.token = Token(TokenTypes.IDENTIFIER, self.line, self.column, kw_or_id, )

    def read_keyword_or_identifier(self):
        chars = []
        while self.char.isalpha() or self.char.isdigit() or self.char == '_':
            chars.append(self.char)
            if len(chars) > self.TOKEN_MAX_LENGTH:
                raise TokenTooLongError(self.line, self.column)
            char = self
            self.char = self.source.get_next_char()
        return ''.join(chars)

    def build_number(self):
        number = self.read_number()
        # checks the occurrence of '.' in number
        if number.count('.') > 1:
            raise InvalidNumberTokenError(self.source.line, self.source.column)
        self.token = Token(TokenTypes.NUMBER, self.line, self.column, number)
        self.token.set_numerical_value()

    def read_number(self):
        chars = []
        while self.char.isdigit() or self.char == '.':
            chars.append(self.char)
            if len(chars) > self.TOKEN_MAX_LENGTH:
                raise TokenTooLongError(self.source.line, self.source.column)
            self.char = self.source.get_next_char()
        return ''.join(chars)

    def build_string(self):
        string = self.read_string()
        self.token = Token(TokenTypes.STRING, self.line, self.column, string)

    def read_string(self):
        chars = [self.char]
        self.char = self.source.get_next_char()
        while self.char != '"':
            # TODO Checking EOT
            chars.append(self.char)
            if len(chars) > self.STRING_MAX_LENGTH:
                raise StringTooLongError(self.source.line, self.source.column)
            self.char = self.source.get_next_char()
        chars.append(self.char)
        self.char = self.source.get_next_char()
        return ''.join(chars)

    def try_to_build_single_operator(self):
        if self.char in Tokens.single_operators.keys():
            print("ZZZZZZZZZ")
            print(self.char)
            self.token = Token(Tokens.single_operators[self.char], self.line, self.column)
            print(self.token.type)
            self.char = self.source.get_next_char()
            return True
        return False

    def try_to_build_double_operator(self):
        for double_operator in Tokens.double_operators.keys():
            if self.char == double_operator[0]:
                second_char = self.source.get_next_char()
                if second_char == double_operator[1]:
                    operator = double_operator
                    self.char = second_char
                    self.token = Token(Tokens.double_operators[operator], self.line, self.column)
                    self.char = self.source.get_next_char()
                    return True
        return False

    def skip_spaces(self):
        while self.char.isspace():
            self.char = self.source.get_next_char()

    def skip_comment(self):
        while self.char != '\n' and self.char != '':
            self.char = self.source.get_next_char()
        self.skip_spaces()
        self.build_token()

    def is_eof(self):
        return self.char == ''




