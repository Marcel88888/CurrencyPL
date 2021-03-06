import copy
from .scope import ScopeManager
from .utils import *
from ..lexer.token_types import TokenTypes
from ..exceptions.exceptions import MainNotDeclaredError, CurrencyNotDefinedError, InvalidVariableTypeError, \
    GetCurrencyError, DivisionZeroError, CurrencyUsedForDecimalVariableError, IllicitOperationError


class Interpreter:
    def __init__(self, parser):
        self.parser = parser
        self.scope_manager = ScopeManager()

    def interpret(self):
        self.parser.parse_program()
        self.parser.program.accept(self)

    def visit_program(self, program):
        main_declared = False
        for function_def in program.function_defs:
            function_def.accept(self)
            if function_def.signature.id == "main":
                main_declared = True
        if not main_declared:
            raise MainNotDeclaredError()
        for function_def in program.function_defs:
            if function_def.signature.id == "main":
                function_def.block.accept(self)

    def visit_function_def(self, function_def):
        self.scope_manager.add_function(function_def.signature.id, function_def)

    def visit_block(self, block):
        for statement in block.statements:
            statement.accept(self)
            if self.scope_manager.return_result is not None:
                return

    def visit_if_statement(self, if_statement):
        if_statement.condition.accept(self)
        if self.scope_manager.last_result:
            if_statement.block1.accept(self)
        else:
            if_statement.block2.accept(self)

    def visit_while_statement(self, while_statement):
        while_statement.condition.accept(self)
        while self.scope_manager.last_result:
            while_statement.block.accept(self)
            while_statement.condition.accept(self)

    def visit_return_statement(self, return_statement):
        return_statement.expression.accept(self)
        self.scope_manager.return_result = self.scope_manager.last_result

    def visit_init_statement(self, init_statement):  # signature, [ assignmentOp, expression ], “;” ;
        name = init_statement.signature.id
        if init_statement.signature.type == TokenTypes.DECIMAL:
            if init_statement.expression is not None:
                init_statement.expression.accept(self)
                if isinstance(self.scope_manager.last_result, CurrencyVariable):
                    raise CurrencyUsedForDecimalVariableError()
                else:
                    variable = DecimalVariable(name, self.scope_manager.last_result.value)
                    self.scope_manager.add_variable(name, variable)
            else:
                self.scope_manager.add_variable(name, DecimalVariable(name))
        elif init_statement.signature.type == TokenTypes.CURRENCY:
            if init_statement.expression is not None:
                init_statement.expression.accept(self)
                if not isinstance(self.scope_manager.last_result, CurrencyVariable):
                    raise CurrencyNotDefinedError(name)
                variable = CurrencyVariable(name, self.scope_manager.last_result.value,
                                            self.scope_manager.last_result.currency)
                self.scope_manager.add_variable(name, variable)
            else:
                self.scope_manager.add_variable(name, CurrencyVariable(name))
        else:
            raise InvalidVariableTypeError(name)

    def visit_assign_statement(self, assign_statement):
        name = assign_statement.id
        assign_statement.expression.accept(self)
        self.scope_manager.last_result.name = name
        self.scope_manager.update_variable(name, self.scope_manager.last_result)

    def visit_print_statement(self, print_statement):
        print_string = ''
        for printable in print_statement.printables:
            if isinstance(printable, str):
                printable = printable.replace('"', '')
                print_string += printable
            else:
                printable.accept(self)
                print_string += str(self.scope_manager.last_result.value)
        self.scope_manager.last_result = print_string  # only for testing
        print(print_string)

    def visit_function_call(self, function_call):
        name = function_call.id
        function = self.scope_manager.get_function(name)
        arguments = []
        for expression in function_call.arguments.expressions:
            expression.accept(self)
            arguments.append(self.scope_manager.last_result)
        self.execute_function(function, arguments)

    def visit_expression(self, expression):  # multiplExpr, { additiveOp, multiplExpr } ;
        expression.multipl_exprs[0].accept(self)
        result = self.scope_manager.last_result
        for additive_op, multipl_expr in zip(expression.additive_ops, expression.multipl_exprs[1:]):
            multipl_expr.accept(self)
            if isinstance(self.scope_manager.last_result, DecimalVariable):
                if isinstance(result, DecimalVariable):
                    if additive_op == TokenTypes.PLUS:
                        result.value += self.scope_manager.last_result.value
                    elif additive_op == TokenTypes.MINUS:
                        result.value -= self.scope_manager.last_result.value
                    self.scope_manager.last_result = result
                elif isinstance(result, CurrencyVariable):
                    raise IllicitOperationError()
            elif isinstance(self.scope_manager.last_result, CurrencyVariable):
                if isinstance(result, CurrencyVariable):
                    self.scope_manager.last_result.exchange(result.currency)
                    if additive_op == TokenTypes.PLUS:
                        result.value += self.scope_manager.last_result.value
                    elif additive_op == TokenTypes.MINUS:
                        result.value -= self.scope_manager.last_result.value
                    self.scope_manager.last_result = result
                elif isinstance(result, DecimalVariable):
                    raise IllicitOperationError()

    def visit_multipl_expr(self, multipl_expr):  # primaryExpr, { multiplOp, primaryExpr } ;
        currency = None
        multipl_expr.primary_exprs[0].accept(self)
        if isinstance(self.scope_manager.last_result, CurrencyVariable):
            currency = self.scope_manager.last_result.currency
        result = self.scope_manager.last_result
        for multipl_op, primary_expr in zip(multipl_expr.multipl_ops, multipl_expr.primary_exprs[1:]):
            primary_expr.accept(self)
            if multipl_op == TokenTypes.MULTIPLY:
                if isinstance(self.scope_manager.last_result, DecimalVariable):
                    result.value *= self.scope_manager.last_result.value
                    if isinstance(result, CurrencyVariable):
                        self.scope_manager.last_result = result
                        return
                elif isinstance(self.scope_manager.last_result, CurrencyVariable):
                    if isinstance(result, CurrencyVariable):
                        raise IllicitOperationError()
                    elif isinstance(result, DecimalVariable):
                        self.scope_manager.last_result.value *= result.value
                        return
            elif multipl_op == TokenTypes.DIVIDE:
                if self.scope_manager.last_result.value == 0:
                    raise DivisionZeroError()
                if isinstance(self.scope_manager.last_result, DecimalVariable):
                    result.value /= self.scope_manager.last_result.value
                    if isinstance(result, CurrencyVariable):
                        self.scope_manager.last_result = result
                        return
                elif isinstance(self.scope_manager.last_result, CurrencyVariable):
                    raise IllicitOperationError()
        if currency is not None:
            self.scope_manager.last_result.currency = currency
        self.scope_manager.last_result.value = result.value

    def visit_primary_expr(self, primary_expr):  # [ “-” ], [currency | getCurrency], ( number | id |
        # parenthExpr | functionCall ), [currency | getCurrency] ;
        currencies = self.check_primary_expr_currency(primary_expr)
        minus = False
        if primary_expr.minus:
            minus = True
        if primary_expr.number is not None:
            if currencies:
                if minus is False:
                    self.scope_manager.last_result = CurrencyVariable('', primary_expr.number, currencies[0])
                else:
                    self.scope_manager.last_result = CurrencyVariable('', -primary_expr.number, currencies[0])
            else:
                if minus is False:
                    self.scope_manager.last_result = DecimalVariable('', primary_expr.number)
                else:
                    self.scope_manager.last_result = DecimalVariable('', -primary_expr.number)
        elif primary_expr.id is not None:
            variable = self.scope_manager.get_variable(primary_expr.id)
            var = copy.copy(variable)
            if currencies:
                for currency in currencies[1:]:  # first is variable own currency
                    var.exchange(currency)
            self.scope_manager.last_result = var
            if minus is True:
                self.scope_manager.last_result.value *= -1
        elif primary_expr.parenth_expr is not None:
            primary_expr.parenth_expr.accept(self)
            if currencies:
                for currency in currencies:
                    self.scope_manager.last_result.exchange(currency)
            if minus is True:
                self.scope_manager.last_result.value *= -1
        elif primary_expr.function_call is not None:
            primary_expr.function_call.accept(self)
            if minus is True:
                self.scope_manager.last_result.value *= -1

    def check_primary_expr_currency(self, primary_expr):
        currencies = []
        if primary_expr is not None:
            if primary_expr.id is not None or primary_expr.parenth_expr is not None:
                if primary_expr.id is not None:
                    _id = primary_expr.id
                    variable = self.scope_manager.get_variable(_id)
                    if isinstance(variable, CurrencyVariable):
                        currencies.append(variable.currency)
            if primary_expr.currency1 is not None or primary_expr.get_currency1 is not None:
                if primary_expr.currency1 is not None:
                    currencies.append(primary_expr.currency1)
                else:
                    primary_expr.get_currency1.accept(self)
                    currencies.append(self.scope_manager.last_result)
            if primary_expr.currency2 is not None or primary_expr.get_currency2 is not None:
                if primary_expr.currency2 is not None:
                    currencies.append(primary_expr.currency2)
                else:
                    primary_expr.get_currency2.accept(self)
                    currencies.append(self.scope_manager.last_result)
        return currencies

    def visit_parenth_expr(self, parenth_expr):  # “(”, expression, “)” ;
        parenth_expr.expression.accept(self)

    def visit_condition(self, condition):  # andCond, { orOp, andCond } ;
        for and_cond in condition.and_conds:
            and_cond.accept(self)
            if self.scope_manager.last_result:
                return

    def visit_and_cond(self, and_cond):  # equalityCond, { andOp, equalityCond } ;
        result = True
        for equality_cond in and_cond.equality_conds:
            equality_cond.accept(self)
            if not self.scope_manager.last_result:
                result = False
        self.scope_manager.last_result = result

    def visit_equality_cond(self, equality_condition):  # relationalCond, [ equalOp, relationalCond ] ;
        result = False
        unary_op = False
        equality_condition.relational_cond1.accept(self)
        if isinstance(self.scope_manager.last_result, bool):
            if self.scope_manager.last_result:
                result = True
        elif isinstance(self.scope_manager.last_result, tuple):  # for 'not' operator
            unary_op = True
            result = self.scope_manager.last_result
        else:
            result = self.scope_manager.last_result
        if equality_condition.equal_op is not None:
            result = False
            equality_condition.relational_cond1.accept(self)
            if isinstance(self.scope_manager.last_result, tuple):  # for 'not' operator
                result1 = self.scope_manager.last_result[1]
            else:
                result1 = self.scope_manager.last_result
            equality_condition.relational_cond2.accept(self)
            result2 = self.scope_manager.last_result
            if isinstance(result1, CurrencyVariable) and isinstance(result2, CurrencyVariable):
                result2.exchange(result1.currency)
            if equality_condition.equal_op == TokenTypes.EQUAL:
                if result1.value == result2.value and unary_op is False \
                        or result1.value != result2.value and unary_op is True:
                    result = True
            elif equality_condition.equal_op == TokenTypes.NOT_EQUAL:
                if result1.value != result2.value and unary_op is False \
                        or result1.value == result2.value and unary_op is True:
                    result = True
        self.scope_manager.last_result = result

    def visit_relational_cond(self, relational_cond):  # primaryCond, [ relationOp, primaryCond ];
        result = False
        unary_op = False
        relational_cond.primary_cond1.accept(self)
        if isinstance(self.scope_manager.last_result, bool):
            if self.scope_manager.last_result:
                result = True
        elif isinstance(self.scope_manager.last_result, tuple):  # for 'not' operator
            unary_op = True
            result = self.scope_manager.last_result
        else:
            result = self.scope_manager.last_result
        if relational_cond.relation_op is not None:
            result = False
            relational_cond.primary_cond1.accept(self)
            if isinstance(self.scope_manager.last_result, tuple):  # for 'not' operator
                result1 = self.scope_manager.last_result[1]
            else:
                result1 = self.scope_manager.last_result
            relational_cond.primary_cond2.accept(self)
            result2 = self.scope_manager.last_result
            if isinstance(result1, CurrencyVariable) and isinstance(result2, CurrencyVariable):
                result2.exchange(result1.currency)
            if relational_cond.relation_op == TokenTypes.GREATER_THAN:
                if result1.value > result2.value and unary_op is False \
                        or result1.value <= result2.value and unary_op is True:
                    result = True
            elif relational_cond.relation_op == TokenTypes.LESS_THAN:
                if result1.value < result2.value and unary_op is False \
                        or result1.value >= result2.value and unary_op is True:
                    result = True
            elif relational_cond.relation_op == TokenTypes.GREATER_OR_EQUAL:
                if result1.value >= result2.value and unary_op is False \
                        or result1.value < result2.value and unary_op is True:
                    result = True
            elif relational_cond.relation_op == TokenTypes.LESS_OR_EQUAL:
                if result1.value <= result2.value and unary_op is False \
                        or result1.value > result2.value and unary_op is True:
                    result = True
        self.scope_manager.last_result = result

    def visit_primary_cond(self, primary_cond):  # [ unaryOp ], ( parenthCond | expression ) ;
        result = False
        if primary_cond.parenth_cond is not None:
            primary_cond.parenth_cond.accept(self)
            if self.scope_manager.last_result:
                result = True
            if primary_cond.unary_op:
                result = not result
            self.scope_manager.last_result = result
        elif primary_cond.expression is not None:
            primary_cond.expression.accept(self)
            if primary_cond.unary_op:
                self.scope_manager.last_result = primary_cond.unary_op, self.scope_manager.last_result

    def visit_parenth_cond(self, parenth_cond):
        parenth_cond.condition.accept(self)

    def visit_get_currency(self, get_currency):
        variable = self.scope_manager.get_variable(get_currency.id)
        if isinstance(variable, CurrencyVariable):
            self.scope_manager.last_result = variable.currency
        else:
            raise GetCurrencyError(get_currency.id)

    def execute_function(self, function, arguments):
        check_arguments(function, arguments)
        self.scope_manager.create_new_scope_and_switch(function)
        self.add_arguments_to_function_scope(function, arguments)
        function.block.accept(self)
        check_returned_type(function, self.scope_manager.return_result)
        self.scope_manager.switch_to_parent_context()

    def add_arguments_to_function_scope(self, function, arguments):
        for argument, parameter_signature in zip(arguments, function.parameters.signatures):
            self.scope_manager.add_variable(parameter_signature.id, argument)
