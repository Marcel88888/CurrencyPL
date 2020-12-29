from src.lexer.token_types import TokenTypes
from src.exceptions.exceptions import _SyntaxError
from .grammar import *


class Parser:
    def __init__(self, lexer):
        self.__lexer = lexer
        self.__function_data_types = [TokenTypes.DECIMAL, TokenTypes.CURRENCY, TokenTypes.VOID]

    def parse_program(self):
        function_defs = []
        function_def = self.parse_function_def()
        while function_def is not None:
            function_defs.append(function_def)
            function_def = self.parse_function_def()

    def parse_function_def(self):  # signature, “(”, parameters, “)”, “{“, block, “}” ;
        self.__lexer.get_next_token()
        signature = self.parse_signature()
        if signature is not None:
            self.__lexer.get_next_token()
            if self.__lexer.token.type == TokenTypes.OP_BRACKET:
                self.__lexer.get_next_token()
                parameters = self.parse_parameters()
                if parameters is not None:
                    self.__lexer.get_next_token()
                    if self.__lexer.token.type == TokenTypes.CL_BRACKET:
                        self.__lexer.get_next_token()
                        if self.__lexer.token.type == TokenTypes.OP_CURLY_BRACKET:
                            self.__lexer.get_next_token()
                            block = self.parse_block()
                            if block is not None:
                                self.__lexer.get_next_token()
                                if self.__lexer.token.type == TokenTypes.CL_CURLY_BRACKET:
                                    return FunctionDef(signature, parameters, block)
                return _SyntaxError(self.__lexer.line, self.__lexer.column)
        return None

    def parse_signature(self):
        token_type = self.__lexer.token.type
        if token_type in self.__function_data_types:
            _type = token_type
            self.__lexer.get_next_token()
            if self.__lexer.token.type == TokenTypes.IDENTIFIER:
                _id = self.__lexer.token.value
                return Signature(_type, _id)
        return None

    def parse_parameters(self):  # [ signature, { “,”, signature } ];
        self.__lexer.get_next_token()


    def parse_block(self):
        return None