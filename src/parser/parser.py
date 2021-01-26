from ..exceptions.exceptions import SyntaxxError
from .grammar import *


class Parser:
    def __init__(self, lexer):
        self.__lexer = lexer
        self.program = None
        self.__lexer.get_next_token()
        self.__function_data_types = [TokenTypes.DECIMAL, TokenTypes.CURRENCY, TokenTypes.VOID]
        self.__relation_ops = [TokenTypes.GREATER_THAN, TokenTypes.LESS_THAN, TokenTypes.GREATER_OR_EQUAL,
                               TokenTypes.LESS_OR_EQUAL]

    def parse_program(self):
        function_defs = []
        function_def = self.parse_function_def()
        while function_def:
            function_defs.append(function_def)
            function_def = self.parse_function_def()
        self.program = Program(function_defs)

    def parse_function_def(self):  # signature, “(”, parameters, “)”, “{“, block, “}” ;
        signature = self.parse_signature()
        if signature:
            self.__lexer.get_next_token()
            if self.__lexer.token.type == TokenTypes.OP_BRACKET:
                self.__lexer.get_next_token()
                parameters = self.parse_parameters()
                print(parameters)
                if parameters:
                    print('1')
                    if self.__lexer.token.type == TokenTypes.CL_BRACKET:
                        print('2')
                        self.__lexer.get_next_token()
                        if self.__lexer.token.type == TokenTypes.OP_CURLY_BRACKET:
                            print('3')
                            self.__lexer.get_next_token()
                            block = self.parse_block()
                            if block:
                                print('4')
                                print(self.__lexer.token.type)
                                if self.__lexer.token.type == TokenTypes.CL_CURLY_BRACKET:
                                    print('5')
                                    self.__lexer.get_next_token()
                                    return FunctionDef(signature, parameters, block)
            raise SyntaxxError(self.__lexer.line, self.__lexer.column)
        return None

    def parse_signature(self):  # type, id ;
        token_type = self.__lexer.token.type
        if token_type in self.__function_data_types:
            _type = token_type
            self.__lexer.get_next_token()
            if self.__lexer.token.type == TokenTypes.IDENTIFIER:
                _id = self.__lexer.token.value
                return Signature(_type, _id)
            raise SyntaxxError(self.__lexer.line, self.__lexer.column)
        return None

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
                    raise SyntaxxError(self.__lexer.line, self.__lexer.column)
        return Parameters(signatures)

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
                    raise SyntaxxError(self.__lexer.line, self.__lexer.column)
        return Arguments(expressions)

    def parse_block(self):  # { statement };
        statements = []
        statement = self.parse_statement()
        while statement:
            statements.append(statement)
            statement = self.parse_statement()
        return Block(statements)

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
            if isinstance(statement, FunctionCall):
                if self.__lexer.token.type == TokenTypes.SEMICOLON:
                    self.__lexer.get_next_token()
                    return statement
                else:
                    raise SyntaxxError(self.__lexer.line, self.__lexer.column)
            return statement
        statement = self.parse_print_statement()
        if statement:
            return statement
        return None

    def parse_if_statement(self):  # “if”, “(”, condition, “)”, “{“, block, “}“, [“else”, “{”, block, “}” ];
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
                            block1 = self.parse_block()
                            if block1:
                                if self.__lexer.token.type == TokenTypes.CL_CURLY_BRACKET:
                                    self.__lexer.get_next_token()
                                    if self.__lexer.token.type == TokenTypes.ELSE:
                                        self.__lexer.get_next_token()
                                        if self.__lexer.token.type == TokenTypes.OP_CURLY_BRACKET:
                                            self.__lexer.get_next_token()
                                            block2 = self.parse_block()
                                            if block2:
                                                if self.__lexer.token.type == TokenTypes.CL_CURLY_BRACKET:
                                                    self.__lexer.get_next_token()
                                                    return IfStatement(condition, block1, block2)
                                        raise SyntaxxError(self.__lexer.line, self.__lexer.column)
                                    return IfStatement(condition, block1)
            raise SyntaxxError(self.__lexer.line, self.__lexer.column)
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
                                    self.__lexer.get_next_token()
                                    return WhileStatement(condition, block)
            raise SyntaxxError(self.__lexer.line, self.__lexer.column)
        return None

    def parse_return_statement(self):  # “return”, expression, “;” ;
        if self.__lexer.token.type == TokenTypes.RETURN:
            self.__lexer.get_next_token()
            expression = self.parse_expression()
            if expression:
                if self.__lexer.token.type == TokenTypes.SEMICOLON:
                    self.__lexer.get_next_token()
                    return ReturnStatement(expression)
            raise SyntaxxError(self.__lexer.line, self.__lexer.column)
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
                        self.__lexer.get_next_token()
                        return InitStatement(signature, expression)
                raise SyntaxxError(self.__lexer.line, self.__lexer.column)
            else:
                if self.__lexer.token.type == TokenTypes.SEMICOLON:
                    self.__lexer.get_next_token()
                    return InitStatement(signature)
            raise SyntaxxError(self.__lexer.line, self.__lexer.column)
        return None

    def parse_print_statement(self):  # “print”, “(“, printable { “,”, printable }, “)”, ";" ;
        if self.__lexer.token.type == TokenTypes.PRINT:
            self.__lexer.get_next_token()
            if self.__lexer.token.type == TokenTypes.OP_BRACKET:
                self.__lexer.get_next_token()
                printables = []
                if self.__lexer.token.type == TokenTypes.STRING:
                    printable = self.__lexer.token.value
                    self.__lexer.get_next_token()
                else:
                    printable = self.parse_expression()
                if printable:
                    printables.append(printable)
                    while self.__lexer.token.type == TokenTypes.COMMA:
                        self.__lexer.get_next_token()
                        if self.__lexer.token.type == TokenTypes.STRING:
                            printable = self.__lexer.token.value
                            self.__lexer.get_next_token()
                        else:
                            printable = self.parse_expression()
                        if printable:
                            printables.append(printable)
                        else:
                            raise SyntaxxError(self.__lexer.line, self.__lexer.column)
                    if self.__lexer.token.type == TokenTypes.CL_BRACKET:
                        self.__lexer.get_next_token()
                        if self.__lexer.token.type == TokenTypes.SEMICOLON:
                            self.__lexer.get_next_token()
                            return PrintStatement(printables)
            raise SyntaxxError(self.__lexer.line, self.__lexer.column)
        return None

    def parse_assign_statement(self, _id):  # id, assignmentOp, expression, “;” ;
        if self.__lexer.token.type == TokenTypes.ASSIGNMENT:
            self.__lexer.get_next_token()
            expression = self.parse_expression()
            if expression:
                if self.__lexer.token.type == TokenTypes.SEMICOLON:
                    self.__lexer.get_next_token()
                    return AssignStatement(_id, expression)
        return None

    def parse_function_call(self, _id):  # id, “(“, arguments, “)”;
        if self.__lexer.token.type == TokenTypes.OP_BRACKET:
            self.__lexer.get_next_token()
            arguments = self.parse_arguments()
            if arguments:
                if self.__lexer.token.type == TokenTypes.CL_BRACKET:
                    self.__lexer.get_next_token()
                    return FunctionCall(_id, arguments)
        return None

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
                    raise SyntaxxError(self.__lexer.line, self.__lexer.column)
            return Condition(and_conds)
        return None

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
                    raise SyntaxxError(self.__lexer.line, self.__lexer.column)
            return AndCond(equality_conds)
        return None

    def parse_equality_cond(self):  # relationalCond, [ equalOp, relationalCond ] ;
        relational_cond1 = self.parse_relational_cond()
        if relational_cond1:
            if self.__lexer.token.type == TokenTypes.EQUAL or self.__lexer.token.type == TokenTypes.NOT_EQUAL:
                equal_op = self.__lexer.token.type
                self.__lexer.get_next_token()
                relational_cond2 = self.parse_relational_cond()
                if relational_cond2:
                    return EqualityCond(relational_cond1, equal_op, relational_cond2)
                raise SyntaxxError(self.__lexer.line, self.__lexer.column)
            return EqualityCond(relational_cond1)
        return None

    def parse_relational_cond(self):  # primaryCond, [ relationOp, primaryCond ];
        primary_cond1 = self.parse_primary_cond()
        if primary_cond1:
            if self.__lexer.token.type in self.__relation_ops:
                relation_op = self.__lexer.token.type
                self.__lexer.get_next_token()
                primary_cond2 = self.parse_primary_cond()
                if primary_cond2:
                    return RelationalCond(primary_cond1, relation_op, primary_cond2)
                raise SyntaxxError(self.__lexer.line, self.__lexer.column)
            return RelationalCond(primary_cond1)
        return None

    def parse_primary_cond(self):  # [ unaryOp ], ( parenthCond | expression ) ;
        unary_op = False
        if self.__lexer.token.type == TokenTypes.NOT:
            unary_op = True
            self.__lexer.get_next_token()
        parenth_cond = self.parse_parenth_cond()
        if parenth_cond:
            self.__lexer.get_next_token()
            return PrimaryCond(unary_op, parenth_cond=parenth_cond)
        expression = self.parse_expression()
        if expression:
            return PrimaryCond(unary_op, expression=expression)
        raise SyntaxxError(self.__lexer.line, self.__lexer.column)

    def parse_parenth_cond(self):  # “(“, condition, “)” ;
        if self.__lexer.token.type == TokenTypes.OP_BRACKET:
            self.__lexer.get_next_token()
            condition = self.parse_condition()
            if condition:
                if self.__lexer.token.type == TokenTypes.CL_BRACKET:
                    return ParenthCond(condition)
            raise SyntaxxError(self.__lexer.line, self.__lexer.column)
        return None

    def parse_expression(self):  # multiplExpr, { additiveOp, multiplExpr } ;
        multipl_exprs = []
        additive_ops = []
        multipl_expr = self.parse_multipl_expr()
        if multipl_expr:
            multipl_exprs.append(multipl_expr)
            while self.__lexer.token.type == TokenTypes.PLUS or self.__lexer.token.type == TokenTypes.MINUS:
                additive_ops.append(self.__lexer.token.type)
                self.__lexer.get_next_token()
                multipl_expr = self.parse_multipl_expr()
                if multipl_expr:
                    multipl_exprs.append(multipl_expr)
                else:
                    raise SyntaxxError(self.__lexer.line, self.__lexer.column)
            return Expression(multipl_exprs, additive_ops)
        return None

    def parse_multipl_expr(self):  # primaryExpr, { multiplOp, primaryExpr } ;
        primary_exprs = []
        multipl_ops = []
        primary_expr = self.parse_primary_expr()
        if primary_expr:
            primary_exprs.append(primary_expr)
            while self.__lexer.token.type == TokenTypes.MULTIPLY or self.__lexer.token.type == TokenTypes.DIVIDE:
                multipl_ops.append(self.__lexer.token.type)
                self.__lexer.get_next_token()
                primary_expr = self.parse_primary_expr()
                if primary_expr:
                    primary_exprs.append(primary_expr)
                else:
                    raise SyntaxxError(self.__lexer.line, self.__lexer.column)
            return MultiplExpr(primary_exprs, multipl_ops)
        return None

    def parse_primary_expr(self):  # [ “-” ], [currency | getCurrency], ( number | id | parenthExpr | functionCall ),
        minus = False
        currency1 = None
        get_currency1 = None
        _id = None
        number = None
        parenth_expr = None
        function_call = None
        counter = 0
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
            _id2 = self.__lexer.token.value
            self.__lexer.get_next_token()
            function_call2 = self.parse_function_call(_id2)
            if function_call2:
                _id2 = None
                function_call = function_call2
            else:
                _id = _id2
        if number is None and not _id and not function_call:  # "is None" with number because number can be 0 and then
            # "if not number" is True
            parenth_expr = self.parse_parenth_expr()
            if not parenth_expr:
                return None
        alternatives = [number, _id, parenth_expr, function_call]
        for alternative in alternatives:
            if alternative is not None:
                counter += 1
        if counter > 1:
            raise SyntaxxError(self.__lexer.line, self.__lexer.column)
        currency2 = None
        get_currency2 = None
        if self.__lexer.token.type == TokenTypes.CURRENCY_TYPE:
            currency2 = self.__lexer.token.value
            self.__lexer.get_next_token()
        elif self.__lexer.token.type == TokenTypes.IDENTIFIER:
            get_currency2 = self.parse_get_currency()
            self.__lexer.get_next_token()
        return PrimaryExpr(minus, currency1, get_currency1, number, _id, parenth_expr, function_call, currency2,
                           get_currency2)

    def parse_parenth_expr(self):  # “(”, expression, “)” ;
        if self.__lexer.token.type == TokenTypes.OP_BRACKET:
            self.__lexer.get_next_token()
            expression = self.parse_expression()
            if expression:
                if self.__lexer.token.type == TokenTypes.CL_BRACKET:
                    self.__lexer.get_next_token()
                    return ParenthExpr(expression)
            raise SyntaxxError(self.__lexer.line, self.__lexer.column)
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

