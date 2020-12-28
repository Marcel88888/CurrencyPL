from src.lexer.token_types import TokenTypes
from src.exceptions.exceptions import _SyntaxError
from .grammar import *


class Parser:
    def __init__(self, lexer):
        self.__lexer = lexer

    def parse_program(self):
        function_defs = []
        function_def = self.parse_function_def()
        while function_def is not None:
            function_defs.append(function_def)
            function_def = self.parse_function_def()

    def parse_function_def(self):  # signature, “(”, parameters, “)”, “{“, block, “}” ;
        token_type = self.__lexer.token.type
        if token_type == TokenTypes.DECIMAL or token_type == TokenTypes.CURRENCY or token_type == TokenTypes.VOID:
            _type = token_type
            self.__lexer.get_next_token()
            if self.__lexer.token.type == TokenTypes.IDENTIFIER:
                _id = self.__lexer.token.value
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
                                        return FunctionDef(_type, _id, parameters, block)
                                    else:
                                        raise _SyntaxError(self.__lexer.line, self.__lexer.column)
                                else:
                                    raise _SyntaxError(self.__lexer.line, self.__lexer.column)
                            else:
                                raise _SyntaxError(self.__lexer.line, self.__lexer.column)
                        else:
                            raise _SyntaxError(self.__lexer.line, self.__lexer.column)
                    else:
                        raise _SyntaxError(self.__lexer.line, self.__lexer.column)
                else:
                    return None
            else:
                return None
        else:
            return None

    def parse_parameters(self):
        return None

    def parse_block(self):
        return None