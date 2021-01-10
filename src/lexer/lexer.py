from .token import Token
from .tokens import Tokens
from .token_types import TokenTypes
from ..exceptions.exceptions import *


class Lexer:
    def __init__(self, source, currencies=None):
        self.__source = source
        self.__currencies = currencies
        self.__source.move_carr_one_pos()
        self.__char = self.__source.character
        self.token = None
        self.line = None
        self.column = None
        self.__TOKEN_MAX_LENGTH = 50
        self.__STRING_MAX_LENGTH = 1000

    def get_next_token(self):
        self.skip_spaces()
        self.line = self.__source.line
        self.column = self.__source.column - 1
        self.build_token()

    def build_token(self):
        if self.is_eof():
            self.token = Token(TokenTypes.EOT, self.line, self.column)
        elif self.__char.isalpha():
            self.build_keyword_or_identifier()
        elif self.__char.isdigit():
            self.build_number()
        elif self.__char == '"':
            self.build_string()
        elif self.__char == '#':
            self.skip_comment()
            self.skip_spaces()
            self.build_token()
        elif self.try_to_build_double_operator():
            return
        elif self.try_to_build_single_operator():
            return
        else:
            raise InvalidTokenError(self.__source.line, self.__source.column)

    def build_keyword_or_identifier(self):
        kw_or_id = self.read_keyword_or_identifier()
        if kw_or_id in Tokens.keywords:
            # keyword
            self.token = Token(Tokens.keywords[kw_or_id], self.line, self.column)
            if self.token.type == TokenTypes.CURRENCY_TYPE:
                self.token.value = kw_or_id
        else:
            # identifier
            self.token = Token(TokenTypes.IDENTIFIER, self.line, self.column, kw_or_id)

    def read_keyword_or_identifier(self):
        chars = []
        while self.__char.isalpha() or self.__char.isdigit() or self.__char == '_':
            chars.append(self.__char)
            if len(chars) > self.__TOKEN_MAX_LENGTH:
                raise TokenTooLongError(self.line, self.column)
            self.get_next_char()
        return ''.join(chars)

    def build_number(self):
        number = self.read_number()
        self.token = Token(TokenTypes.NUMBER, self.line, self.column, number)
        self.token.set_numerical_value()

    def read_number(self):
        chars = []
        if self.__char in ['1', '2', '3', '4', '5', '6', '7', '8', '9']:
            chars = self.read_digits(chars)
            if self.__char == '.':
                chars.append(self.__char)
                self.get_next_char()
                if self.__char.isdigit():
                    chars = self.read_digits(chars)
        else:   # '0'
            chars.append(self.__char)
            self.get_next_char()
            if self.__char == '.':
                chars.append(self.__char)
                self.get_next_char()
                if self.__char.isdigit():
                    chars = self.read_digits(chars)
        return ''.join(chars)

    def read_digits(self, chars):
        while True:
            chars.append(self.__char)
            if len(chars) > self.__TOKEN_MAX_LENGTH:
                raise TokenTooLongError(self.__source.line, self.__source.column)
            self.get_next_char()
            if not self.__char.isdigit():
                break
        return chars

    def build_string(self):
        string = self.read_string()
        self.token = Token(TokenTypes.STRING, self.line, self.column, string)

    def read_string(self):
        chars = [self.__char]
        self.get_next_char()
        while self.__char != '"':
            chars.append(self.__char)
            if len(chars) > self.__STRING_MAX_LENGTH:
                raise StringTooLongError(self.__source.line, self.__source.column)
            self.get_next_char()
        chars.append(self.__char)
        self.get_next_char()
        return ''.join(chars)

    def try_to_build_single_operator(self):
        if self.__char in Tokens.single_operators.keys():
            self.token = Token(Tokens.single_operators[self.__char], self.line, self.column)
            self.get_next_char()
            return True
        return False

    def try_to_build_double_operator(self):
        for double_operator in Tokens.double_operators.keys():
            if self.__char == double_operator[0]:
                position = self.__source.source_stream.tell()
                self.__source.move_carr_one_pos()
                second_char = self.__source.character
                if second_char == double_operator[1]:
                    operator = double_operator
                    self.__char = second_char
                    self.token = Token(Tokens.double_operators[operator], self.line, self.column)
                    self.get_next_char()
                    return True
                else:
                    self.__source.source_stream.seek(position)
        return False

    def skip_spaces(self):
        while self.__char.isspace():
            self.get_next_char()

    def skip_comment(self):
        while self.__char != '\n' and self.__char != '':
            self.get_next_char()

    def get_next_char(self):
        self.__source.move_carr_one_pos()
        self.__char = self.__source.character

    def is_eof(self):
        return self.__char == ''
