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

    def parse_signature(self):  # type, id ;
        token_type = self.__lexer.token.type
        if token_type in self.__function_data_types:
            _type = token_type
            self.__lexer.get_next_token()
            if self.__lexer.token.type == TokenTypes.IDENTIFIER:
                _id = self.__lexer.token.value
                return Signature(_type, _id)
            raise _SyntaxError(self.__lexer.line, self.__lexer.column)
        return None

    def parse_parameters(self):  # [ signature, { “,”, signature } ];
        signatures = []
        signature = self.parse_signature()
        if signature is not None:
            signatures.append(signature)
            self.__lexer.get_next_token()
            while self.__lexer.token.type == TokenTypes.COMMA:
                self.__lexer.get_next_token()
                signature = self.parse_signature()
                if signature is not None:
                    signatures.append(signature)
                else:
                    raise _SyntaxError(self.__lexer.line, self.__lexer.column)
                self.__lexer.get_next_token()
            return Parameters(signatures)
        return None

    def parse_block(self):  # { statement };
        statements = []
        statement = self.parse_statement()
        while statement is not None:
            statements.append(statement)
            self.__lexer.get_next_token()
            statement = self.parse_statement()
        return Block(statements)

    def parse_statement(self):  # ifStatement | whileStatement | returnStatement | initStatement | assignStatement |
        # functionCall ;
        statement = self.parse_if_statement()
        if statement is not None:
            return statement
        statement = self.parse_while_statement()
        if statement is not None:
            return statement
        statement = self.parse_return_statement()
        if statement is not None:
            return statement
        statement = self.parse_init_statement()
        if statement is not None:
            return statement
        statement = self.parse_assign_statement()
        if statement is not None:
            return statement
        statement = self.parse_function_call()
        if statement is not None:
            return statement
        return None

    def parse_if_statement(self):
        pass

    def parse_while_statement(self):
        pass

    def parse_return_statement(self):
        pass

    def parse_init_statement(self):
        pass

    def parse_assign_statement(self):
        pass

    def parse_function_call(self):
        pass
