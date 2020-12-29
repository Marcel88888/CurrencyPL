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

    def parse_arguments(self):  # [ expression { “,”, expression } ] ;
        expressions = []
        expression = self.parse_expression()
        if expression is not None:
            expressions.append(expression)
            self.__lexer.get_next_token()
            while self.__lexer.token.type == TokenTypes.COMMA:
                self.__lexer.get_next_token()
                expression = self.parse_expression()
                if expression is not None:
                    expressions.append(expression)
                else:
                    raise _SyntaxError(self.__lexer.line, self.__lexer.column)
                self.__lexer.get_next_token()
            return Arguments(expressions)
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

    def parse_if_statement(self):  # “if”, “(”, condition, “)”, “{“, block, “}“ ;
        if self.__lexer.token.type == TokenTypes.IF:
            self.__lexer.get_next_token()
            if self.__lexer.token.type == TokenTypes.OP_BRACKET:
                self.__lexer.get_next_token()
                condition = self.parse_condition()
                if condition is not None:
                    self.__lexer.get_next_token()
                    if self.__lexer.token.type == TokenTypes.CL_BRACKET:
                        self.__lexer.get_next_token()
                        if self.__lexer.token.type == TokenTypes.OP_CURLY_BRACKET:
                            block = self.parse_block()
                            if block is not None:
                                self.__lexer.get_next_token()
                                if self.__lexer.token.type == TokenTypes.CL_CURLY_BRACKET:
                                    return IfStatement(condition, block)
            return _SyntaxError(self.__lexer.line, self.__lexer.column)
        return None

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

    def parse_condition(self):  # andCond, { orOp, andCond } ;
        and_conds = []
        and_cond = self.parse_and_cond()
        if and_cond is not None:
            and_conds.append(and_cond)
            self.__lexer.get_next_token()
            while self.__lexer.token.type == TokenTypes.OR:
                self.__lexer.get_next_token()
                and_cond = self.parse_and_cond()
                if and_cond is not None:
                    and_conds.append(and_cond)
                else:
                    raise _SyntaxError(self.__lexer.line, self.__lexer.column)
                self.__lexer.get_next_token()
            return Condition(and_conds)
        return None

    def parse_and_cond(self):  # equalityCond, { andOp, equalityCond } ;
        equality_conds = []
        equality_cond = self.parse_equality_cond()
        if equality_cond is not None:
            equality_conds.append(equality_cond)
            self.__lexer.get_next_token()
            while self.__lexer.token.type == TokenTypes.AND:
                self.__lexer.get_next_token()
                equality_cond = self.parse_equality_cond()
                if equality_cond is not None:
                    equality_conds.append(equality_cond)
                else:
                    raise _SyntaxError(self.__lexer.line, self.__lexer.column)
                self.__lexer.get_next_token()
            return AndCond(equality_conds)
        return None

    def parse_equality_cond(self):  # relationalCond, [ equalOp, relationalCond ] ;
        pass

    def parse_relational_cond(self):  # primaryCond, [ relationOp, primaryCond ];
        pass

    def parse_primary_cond(self):  # [ unaryOp ], ( parentCond | expression ) ;
        pass

    def parse_expression(self):  # multiplExpr, { additiveOp, multiplExpr } ;
        pass
