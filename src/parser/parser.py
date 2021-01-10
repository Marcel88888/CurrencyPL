from ..exceptions.exceptions import _SyntaxError
from ..lexer.token_types import TokenTypes
from .grammar import *
from .program import Program


class Parser:
    def __init__(self, lexer):
        self.__lexer = lexer
        self.program = None
        self.__lexer.get_next_token()
        self.__function_data_types = [TokenTypes.DECIMAL, TokenTypes.CURRENCY, TokenTypes.VOID]
        self.__relation_ops = [TokenTypes.GREATER_THAN, TokenTypes.LESS_THAN, TokenTypes.GREATER_OR_EQUAL,
                               TokenTypes.LESS_OR_EQUAL]

    # TODO test
    def parse_program(self):
        function_defs = []
        function_def = self.parse_function_def()
        while function_def:
            function_defs.append(function_def)
            function_def = self.parse_function_def()
        self.program = Program(function_defs)

    # TODO test
    def parse_function_def(self):  # signature, “(”, parameters, “)”, “{“, block, “}” ;
        signature = self.parse_signature()
        if signature:
            self.__lexer.get_next_token()
            if self.__lexer.token.type == TokenTypes.OP_BRACKET:
                self.__lexer.get_next_token()
                parameters = self.parse_parameters()
                if parameters:
                    if self.__lexer.token.type == TokenTypes.CL_BRACKET:
                        self.__lexer.get_next_token()
                        if self.__lexer.token.type == TokenTypes.OP_CURLY_BRACKET:
                            self.__lexer.get_next_token()
                            block = self.parse_block()
                            if block:
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
        if signature:
            signatures.append(signature)
            self.__lexer.get_next_token()
            while self.__lexer.token.type == TokenTypes.COMMA:
                self.__lexer.get_next_token()
                signature = self.parse_signature()
                if signature:
                    signatures.append(signature)
                    self.__lexer.get_next_token()
                else:
                    raise _SyntaxError(self.__lexer.line, self.__lexer.column)
        return Parameters(signatures)

    # ONE TOKEN MORE (WHILE)
    def parse_arguments(self):  # [ expression { “,”, expression } ] ;
        expressions = []
        expression = self.parse_expression()
        if expression:
            expressions.append(expression)
            while self.__lexer.token.type == TokenTypes.COMMA:
                self.__lexer.get_next_token()
                expression = self.parse_expression()
                if expression:
                    expressions.append(expression)
                else:
                    raise _SyntaxError(self.__lexer.line, self.__lexer.column)
        return Arguments(expressions)

    # ONE TOKEN MORE (WHILE)
    def parse_block(self):  # { statement };
        statements = []
        statement = self.parse_statement()
        while statement:
            statements.append(statement)
            self.__lexer.get_next_token()
            statement = self.parse_statement()
        return Block(statements)

    # TODO test
    def parse_statement(self):  # ifStatement | whileStatement | returnStatement | initStatement | assignStatement |
        # printStatement | (functionCall, ";") ;
        statement = self.parse_if_statement()
        if statement:
            return statement
        statement = self.parse_while_statement()
        if statement:
            return statement
        statement = self.parse_return_statement()
        if statement:
            return statement
        statement = self.parse_init_statement()
        if statement:
            return statement
        statement = self.parse_assign_statement_or_function_call()
        if statement:
            return statement
        statement = self.parse_print_statement()
        if statement:
            return statement
        return None

    def parse_if_statement(self):  # “if”, “(”, condition, “)”, “{“, block, “}“ ;
        if self.__lexer.token.type == TokenTypes.IF:
            self.__lexer.get_next_token()
            if self.__lexer.token.type == TokenTypes.OP_BRACKET:
                self.__lexer.get_next_token()
                condition = self.parse_condition()
                if condition:
                    if self.__lexer.token.type == TokenTypes.CL_BRACKET:
                        self.__lexer.get_next_token()
                        if self.__lexer.token.type == TokenTypes.OP_CURLY_BRACKET:
                            self.__lexer.get_next_token()
                            block = self.parse_block()
                            if block:
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
                if condition:
                    if self.__lexer.token.type == TokenTypes.CL_BRACKET:
                        self.__lexer.get_next_token()
                        if self.__lexer.token.type == TokenTypes.OP_CURLY_BRACKET:
                            self.__lexer.get_next_token()
                            block = self.parse_block()
                            if block:
                                if self.__lexer.token.type == TokenTypes.CL_CURLY_BRACKET:
                                    return WhileStatement(condition, block)
            raise _SyntaxError(self.__lexer.line, self.__lexer.column)
        return None

    def parse_return_statement(self):  # “return”, expression, “;” ;
        if self.__lexer.token.type == TokenTypes.RETURN:
            self.__lexer.get_next_token()
            expression = self.parse_expression()
            if expression:
                if self.__lexer.token.type == TokenTypes.SEMICOLON:
                    return ReturnStatement(expression)
            raise _SyntaxError(self.__lexer.line, self.__lexer.column)
        return None

    def parse_init_statement(self):  # signature, [ assignmentOp, expression ], “;” ;
        signature = self.parse_signature()
        if signature:
            self.__lexer.get_next_token()
            if self.__lexer.token.type == TokenTypes.ASSIGNMENT:
                self.__lexer.get_next_token()
                expression = self.parse_expression()
                if expression:
                    if self.__lexer.token.type == TokenTypes.SEMICOLON:
                        return InitStatement(signature, expression)
                raise _SyntaxError(self.__lexer.line, self.__lexer.column)
            else:
                if self.__lexer.token.type == TokenTypes.SEMICOLON:
                    return InitStatement(signature)
            raise _SyntaxError(self.__lexer.line, self.__lexer.column)
        return None

    # TODO test
    def parse_print_statement(self):  # “print”, “(“, printable { “,”, printable }, “)” ;
        if self.__lexer.token.type == TokenTypes.PRINT:
            self.__lexer.get_next_token()
            if self.__lexer.token.type == TokenTypes.OP_BRACKET:
                self.__lexer.get_next_token()
                printables = []
                if self.__lexer.token.type == TokenTypes.STRING:
                    printable = self.__lexer.token.value
                else:
                    printable = self.parse_expression()
                if printable:
                    printables.append(printable)
                    self.__lexer.get_next_token()
                    while self.__lexer.token.type == TokenTypes.COMMA:
                        self.__lexer.get_next_token()
                        if self.__lexer.token.type == TokenTypes.STRING:
                            printable = self.__lexer.token.value
                        else:
                            printable = self.parse_expression()
                        if printable:
                            printables.append(printable)
                            self.__lexer.get_next_token()
                        else:
                            raise _SyntaxError(self.__lexer.line, self.__lexer.column)
                    if self.__lexer.token.type == TokenTypes.CL_BRACKET:
                        return PrintStatement(printables)
            raise _SyntaxError(self.__lexer.line, self.__lexer.column)
        return None

    def parse_assign_statement(self, _id):  # id, assignmentOp, expression, “;” ;
        if self.__lexer.token.type == TokenTypes.ASSIGNMENT:
            self.__lexer.get_next_token()
            expression = self.parse_expression()
            if expression:
                if self.__lexer.token.type == TokenTypes.SEMICOLON:
                    return AssignStatement(_id, expression)
        return None

    # TODO test
    def parse_function_call(self, _id):  # id, “(“, arguments, “)”;
        if self.__lexer.token.type == TokenTypes.OP_BRACKET:
            self.__lexer.get_next_token()
            arguments = self.parse_arguments()
            if arguments:
                if self.__lexer.token.type == TokenTypes.CL_BRACKET:
                    self.__lexer.get_next_token()
                    return FunctionCall(_id, arguments)
        return None

    # TODO test
    def parse_assign_statement_or_function_call(self):
        if self.__lexer.token.type == TokenTypes.IDENTIFIER:
            _id = self.__lexer.token.value
            self.__lexer.get_next_token()
            statement = self.parse_assign_statement(_id)
            if statement:
                return statement
            statement = self.parse_function_call(_id)
            if statement:
                return statement

    # ONE TOKEN MORE (WHILE)
    def parse_condition(self):  # andCond, { orOp, andCond } ;
        and_conds = []
        and_cond = self.parse_and_cond()
        if and_cond:
            and_conds.append(and_cond)
            while self.__lexer.token.type == TokenTypes.OR:
                self.__lexer.get_next_token()
                and_cond = self.parse_and_cond()
                if and_cond:
                    and_conds.append(and_cond)
                else:
                    raise _SyntaxError(self.__lexer.line, self.__lexer.column)
            return Condition(and_conds)
        return None

    # ONE TOKEN MORE (WHILE)
    def parse_and_cond(self):  # equalityCond, { andOp, equalityCond } ;
        equality_conds = []
        equality_cond = self.parse_equality_cond()
        if equality_cond:
            equality_conds.append(equality_cond)
            while self.__lexer.token.type == TokenTypes.AND:
                self.__lexer.get_next_token()
                equality_cond = self.parse_equality_cond()
                if equality_cond:
                    equality_conds.append(equality_cond)
                else:
                    raise _SyntaxError(self.__lexer.line, self.__lexer.column)
            return AndCond(equality_conds)
        return None

    # ONE TOKEN MORE
    def parse_equality_cond(self):  # relationalCond, [ equalOp, relationalCond ] ;
        relational_cond1 = self.parse_relational_cond()
        if relational_cond1:
            if self.__lexer.token.type == TokenTypes.EQUAL or self.__lexer.token.type == TokenTypes.NOT_EQUAL:
                equal_op = self.__lexer.token.type
                self.__lexer.get_next_token()
                relational_cond2 = self.parse_relational_cond()
                if relational_cond2:
                    return EqualityCond(relational_cond1, equal_op, relational_cond2)
                raise _SyntaxError(self.__lexer.line, self.__lexer.column)
            return EqualityCond(relational_cond1)
        return None

    # ONE TOKEN MORE
    def parse_relational_cond(self):  # primaryCond, [ relationOp, primaryCond ];
        primary_cond1 = self.parse_primary_cond()
        if primary_cond1:
            if self.__lexer.token.type in self.__relation_ops:
                relation_op = self.__lexer.token.type
                self.__lexer.get_next_token()
                primary_cond2 = self.parse_primary_cond()
                if primary_cond2:
                    return RelationalCond(primary_cond1, relation_op, primary_cond2)
                raise _SyntaxError(self.__lexer.line, self.__lexer.column)
            return RelationalCond(primary_cond1)
        return None

    # ONE TOKEN MORE
    def parse_primary_cond(self):  # [ unaryOp ], ( parenthCond | expression ) ;
        unary_op = False
        if self.__lexer.token.type == TokenTypes.NOT:
            unary_op = True
            self.__lexer.get_next_token()
        parenth_cond = self.parse_parenth_cond()
        if parenth_cond:
            self.__lexer.get_next_token()
            return PrimaryCond(unary_op=unary_op, parenth_cond=parenth_cond)
        expression = self.parse_expression()
        if expression:
            return PrimaryCond(unary_op=unary_op, expression=expression)
        raise _SyntaxError(self.__lexer.line, self.__lexer.column)

    def parse_parenth_cond(self):  # “(“, condition, “)” ;
        if self.__lexer.token.type == TokenTypes.OP_BRACKET:
            self.__lexer.get_next_token()
            condition = self.parse_condition()
            if condition:
                if self.__lexer.token.type == TokenTypes.CL_BRACKET:
                    return ParenthCond(condition)
            raise _SyntaxError(self.__lexer.line, self.__lexer.column)
        return None

    # ONE TOKEN MORE (WHILE)
    def parse_expression(self):  # multiplExpr, { additiveOp, multiplExpr } ;
        multipl_exprs = []
        multipl_expr = self.parse_multipl_expr()
        if multipl_expr:
            additive_op = None
            multipl_exprs.append(multipl_expr)
            while self.__lexer.token.type == TokenTypes.PLUS or self.__lexer.token.type == TokenTypes.MINUS:
                additive_op = self.__lexer.token.type
                self.__lexer.get_next_token()
                multipl_expr = self.parse_multipl_expr()
                if multipl_expr:
                    multipl_exprs.append(multipl_expr)
                else:
                    raise _SyntaxError(self.__lexer.line, self.__lexer.column)
            return Expression(multipl_exprs, additive_op)
        return None

    def parse_multipl_expr(self):  # primaryExpr, { multiplOp, primaryExpr } ;
        primary_exprs = []
        primary_expr = self.parse_primary_expr()
        if primary_expr:
            multipl_op = None
            primary_exprs.append(primary_expr)
            while self.__lexer.token.type == TokenTypes.MULTIPLY or self.__lexer.token.type == TokenTypes.DIVIDE:
                multipl_op = self.__lexer.token.type
                self.__lexer.get_next_token()
                primary_expr = self.parse_primary_expr()
                if primary_expr:
                    primary_exprs.append(primary_expr)
                else:
                    raise _SyntaxError(self.__lexer.line, self.__lexer.column)
            return MultiplExpr(primary_exprs, multipl_op)
        return None

    # ONE TOKEN MORE
    def parse_primary_expr(self):  # [ “-” ], [currency | getCurrency], ( number | id | parenthExpr | functionCall ),
        minus = False
        currency1 = None
        get_currency1 = None
        _id = None
        number = None
        parenth_expr = None
        function_call = None
        if self.__lexer.token.type == TokenTypes.MINUS:
            minus = True
            self.__lexer.get_next_token()
        if self.__lexer.token.type == TokenTypes.CURRENCY_TYPE:
            currency1 = self.__lexer.token.value
            self.__lexer.get_next_token()
        elif self.__lexer.token.type == TokenTypes.IDENTIFIER:
            _id = self.__lexer.token.value
            get_currency1 = self.parse_get_currency()
            if get_currency1:
                _id = None
                self.__lexer.get_next_token()
            else:
                function_call = self.parse_function_call(_id)
                if function_call:
                    _id = None
        if self.__lexer.token.type == TokenTypes.NUMBER:
            number = self.__lexer.token.numerical_value
            self.__lexer.get_next_token()
        elif self.__lexer.token.type == TokenTypes.IDENTIFIER:
            _id = self.__lexer.token.value
            self.__lexer.get_next_token()
            function_call = self.parse_function_call(_id)
            if function_call:
                _id = None
        if not number and not _id and not function_call:
            parenth_expr = self.parse_parenth_expr()
            if not parenth_expr:
                raise _SyntaxError(self.__lexer.line, self.__lexer.column)
        currency2 = None
        get_currency2 = None
        if self.__lexer.token.type == TokenTypes.CURRENCY_TYPE:
            currency2 = self.__lexer.token.value
            self.__lexer.get_next_token()
        elif self.__lexer.token.type == TokenTypes.IDENTIFIER:
            get_currency2 = self.parse_get_currency()
            self.__lexer.get_next_token()
        return PrimaryExpr(minus=minus, currency1=currency1, get_currency1=get_currency1, number=number, _id=_id,
                           parenth_expr=parenth_expr, function_call=function_call, currency2=currency2,
                           get_currency2=get_currency2)

    # ONE TOKEN MORE
    def parse_parenth_expr(self):  # “(”, expression, “)” ;
        if self.__lexer.token.type == TokenTypes.OP_BRACKET:
            self.__lexer.get_next_token()
            expression = self.parse_expression()
            if expression:
                if self.__lexer.token.type == TokenTypes.CL_BRACKET:
                    self.__lexer.get_next_token()
                    return ParenthExpr(expression)
            raise _SyntaxError(self.__lexer.line, self.__lexer.column)
        return None

    def parse_get_currency(self):  # id, “.”, “getCurrency()” ;
        if self.__lexer.token.type == TokenTypes.IDENTIFIER:
            _id = self.__lexer.token.value
            self.__lexer.get_next_token()
            if self.__lexer.token.type == TokenTypes.DOT:
                self.__lexer.get_next_token()
                if self.__lexer.token.type == TokenTypes.GET_CURRENCY:
                    self.__lexer.get_next_token()
                    if self.__lexer.token.type == TokenTypes.OP_BRACKET:
                        self.__lexer.get_next_token()
                        if self.__lexer.token.type == TokenTypes.CL_BRACKET:
                            return GetCurrency(_id)
        return None
