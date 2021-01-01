from src.lexer.token_types import TokenTypes
from src.exceptions.exceptions import _SyntaxError
from .grammar import *


class Parser:
    def __init__(self, lexer):
        self.__lexer = lexer
        self.__function_data_types = [TokenTypes.DECIMAL, TokenTypes.CURRENCY, TokenTypes.VOID]
        self.relation_ops = [TokenTypes.GREATER_THAN, TokenTypes.LESS_THAN, TokenTypes.GREATER_OR_EQUAL,
                             TokenTypes.LESS_OR_EQUAL]

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
            raise _SyntaxError(self.__lexer.line, self.__lexer.column)
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

    # ONE TOKEN MORE (WHILE)
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
                    self.__lexer.get_next_token()
                else:
                    raise _SyntaxError(self.__lexer.line, self.__lexer.column)
            return Parameters(signatures)
        return None

    # ONE TOKEN MORE (WHILE)
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
                    self.__lexer.get_next_token()
                else:
                    raise _SyntaxError(self.__lexer.line, self.__lexer.column)
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
        statement = self.parse_assign_statement_or_function_call()
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
                    if self.__lexer.token.type == TokenTypes.CL_BRACKET:
                        self.__lexer.get_next_token()
                        if self.__lexer.token.type == TokenTypes.OP_CURLY_BRACKET:
                            block = self.parse_block()
                            if block is not None:
                                self.__lexer.get_next_token()
                                if self.__lexer.token.type == TokenTypes.CL_CURLY_BRACKET:
                                    return IfStatement(condition, block)
            raise _SyntaxError(self.__lexer.line, self.__lexer.column)
        return None

    def parse_while_statement(self):  # “while”, “(“, condition, “)”, “{“, block, “}“ ;
        if self.__lexer.token.type == TokenTypes.WHILE:
            self.__lexer.get_next_token()
            if self.__lexer.token.type == TokenTypes.OP_BRACKET:
                self.__lexer.get_next_token()
                condition = self.parse_condition()
                if condition is not None:
                    if self.__lexer.token.type == TokenTypes.CL_BRACKET:
                        self.__lexer.get_next_token()
                        if self.__lexer.token.type == TokenTypes.OP_CURLY_BRACKET:
                            self.__lexer.get_next_token()
                            block = self.parse_block()
                            if block is not None:
                                self.__lexer.get_next_token()
                                if self.__lexer.token.type == TokenTypes.CL_CURLY_BRACKET:
                                    return WhileStatement(condition, block)
            raise _SyntaxError(self.__lexer.line, self.__lexer.column)
        return None

    def parse_return_statement(self):  # “return”, expression, “;” ;
        if self.__lexer.token.type == TokenTypes.RETURN:
            self.__lexer.get_next_token()
            expression = self.parse_expression()
            if expression is not None:
                self.__lexer.get_next_token()
                if self.__lexer.token.type == TokenTypes.SEMICOLON:
                    return ReturnStatement(expression)
            raise _SyntaxError(self.__lexer.line, self.__lexer.column)
        return None

    def parse_init_statement(self):  # signature, [ assignmentOp, expression ], “;” ;
        signature = self.parse_signature()
        if signature is not None:
            self.__lexer.get_next_token()
            if self.__lexer.token.type == TokenTypes.ASSIGNMENT:
                self.__lexer.get_next_token()
                expression = self.parse_expression()
                if expression is not None:
                    if self.__lexer.token.type == TokenTypes.SEMICOLON:
                        return InitStatement(signature, expression)
                raise _SyntaxError(self.__lexer.line, self.__lexer.column)
            else:
                if self.__lexer.token.type == TokenTypes.SEMICOLON:
                    return InitStatement(signature)
            raise _SyntaxError(self.__lexer.line, self.__lexer.column)
        return None

    def parse_assign_statement(self, _id):  # id, assignmentOp, expression, “;” ;
        if self.__lexer.token.type == TokenTypes.IDENTIFIER:
            _id = self.__lexer.token.value
            self.__lexer.get_next_token()
            if self.__lexer.token.type == TokenTypes.ASSIGNMENT:
                self.__lexer.get_next_token()
                expression = self.parse_expression()
                if expression is not None:
                    if self.__lexer.token.type == TokenTypes.SEMICOLON:
                        return AssignStatement(_id, expression)
            raise _SyntaxError(self.__lexer.line, self.__lexer.column)
        return None

    def parse_function_call(self, _id):  # id, “(“, arguments, “)”, “;” ;
        if self.__lexer.token.type == TokenTypes.OP_BRACKET:
            self.__lexer.get_next_token()
            arguments = self.parse_arguments()
            if arguments is not None:
                if self.__lexer.token.type == TokenTypes.CL_BRACKET:
                    self.__lexer.get_next_token()
                    if self.__lexer.token.type == TokenTypes.SEMICOLON:
                        return FunctionCall(_id, arguments)
        raise _SyntaxError(self.__lexer.line, self.__lexer.column)

    def parse_assign_statement_or_function_call(self):
        if self.__lexer.token.type == TokenTypes.IDENTIFIER:
            _id = self.__lexer.token.value
            self.__lexer.get_next_token()
            statement = self.parse_assign_statement(_id)
            if statement is not None:
                return statement
            statement = self.parse_function_call(_id)
            if statement is not None:
                return statement

    # ONE TOKEN MORE (WHILE)
    def parse_condition(self):  # andCond, { orOp, andCond } ;
        and_conds = []
        and_cond = self.parse_and_cond()
        if and_cond is not None:
            and_conds.append(and_cond)
            while self.__lexer.token.type == TokenTypes.OR:
                self.__lexer.get_next_token()
                and_cond = self.parse_and_cond()
                if and_cond is not None:
                    and_conds.append(and_cond)
                else:
                    raise _SyntaxError(self.__lexer.line, self.__lexer.column)
            return Condition(and_conds)
        return None

    # ONE TOKEN MORE (WHILE)
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
                    self.__lexer.get_next_token()
                else:
                    raise _SyntaxError(self.__lexer.line, self.__lexer.column)
            return AndCond(equality_conds)
        return None

    def parse_equality_cond(self):  # relationalCond, [ equalOp, relationalCond ] ;
        relational_cond1 = self.parse_relational_cond()
        if relational_cond1 is not None:
            self.__lexer.get_next_token()
            if self.__lexer.token.type == TokenTypes.EQUAL:
                self.__lexer.get_next_token()
                relational_cond2 = self.parse_relational_cond()
                if relational_cond2 is not None:
                    relational_conds = relational_cond1, relational_cond2
                    return EqualityCond(relational_conds)
                raise _SyntaxError(self.__lexer.line, self.__lexer.column)
            return EqualityCond(relational_cond1)
        return None

    def parse_relational_cond(self):  # primaryCond, [ relationOp, primaryCond ];
        primary_cond1 = self.parse_primary_cond()
        if primary_cond1 is not None:
            self.__lexer.get_next_token()
            if self.__lexer.token.type in self.relation_ops:
                self.__lexer.get_next_token()
                primary_cond2 = self.parse_primary_cond()
                if primary_cond2 is not None:
                    primary_conds = primary_cond1, primary_cond2
                    return RelationalCond(primary_conds)
                raise _SyntaxError(self.__lexer.line, self.__lexer.column)
            return EqualityCond(primary_cond1)
        return None

    def parse_primary_cond(self):  # [ unaryOp ], ( parentCond | expression ) ;
        pass

    def parse_parenth_cond(self):  # “(“, condition, “)” ;
        pass

    # ONE TOKEN MORE (WHILE)
    def parse_expression(self):  # multiplExpr, { additiveOp, multiplExpr } ;
        pass

    def parse_multipl_expression(self):  # primaryExpr, { multiplOp, primaryExpr } ;
        pass

    def parse_primary_expr(self):  # [ “-” ], [currency | getCurrency], ( number | id | parenthExpr | functionCall ),
        # [currency | getCurrency] ;
        pass

    def parse_parenth_expr(self):  # “(”, expression, “)” ;
        pass

    def parse_get_currency(self):  # id, “.”, “getCurrency()” ;
        pass

    def parse_string(self):  # “””, { ( anyVisibleChar - “”” ) | “ ” }, “”” ;
        pass

