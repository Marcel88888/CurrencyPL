from .scope import ScopeManager
from .utils import *
from ..lexer.token_types import TokenTypes
from ..exceptions.exceptions import MainNotDeclaredError, CurrencyNotDefinedError, InvalidVariableTypeError, \
    GetCurrencyError, DivisionZeroError, CurrencyUsedForDecimalVariableError


class Interpreter:
    def __init__(self, parser):
        self.parser = parser
        self.scope_manager = ScopeManager()

    # TODO test
    def interpret(self):
        self.parser.program.accept(self)

    # TODO test
    def visit_program(self, program):
        main_declared = False
        for function_def in program.function_defs:
            if function_def.signature.id == "main":
                main_declared = True
                function_def.accept(self)
        if not main_declared:
            raise MainNotDeclaredError

    # TODO test
    def visit_function_def(self, function_def):
        self.scope_manager.add_function(function_def.signature.id, function_def)

    # TODO test
    def visit_block(self, block):
        for statement in block.statements:
            statement.accept(self)

    # TODO test
    def visit_if_statement(self, if_statement):
        if_statement.condition.accept(self)
        if self.scope_manager.last_result:
            for statement in if_statement.block1.statements:
                statement.accept(self)
        else:
            for statement in if_statement.block2.statements:
                statement.accept(self)

    # TODO test
    def visit_while_statement(self, while_statement):
        while_statement.condition.accept(self)
        while self.scope_manager.last_result:
            for statement in while_statement.block.statements:
                statement.accept(self)
            while_statement.condition.accept(self)

    # TODO test
    def visit_return_statement(self, return_statement):
        return_statement.expression.accept(self)

    def visit_init_statement(self, init_statement):  # signature, [ assignmentOp, expression ], “;” ;
        name = init_statement.signature.id
        if init_statement.signature.type == TokenTypes.DECIMAL:
            if init_statement.expression is not None:
                init_statement.expression.accept(self)
                currency = self.check_expression_currency(init_statement.expression)
                if currency is not None:
                    raise CurrencyUsedForDecimalVariableError
                variable = DecimalVariable(name, self.scope_manager.last_result.value)
                self.scope_manager.add_variable(name, variable)
            else:
                self.scope_manager.add_variable(name, DecimalVariable(name))
        elif init_statement.signature.type == TokenTypes.CURRENCY:
            if init_statement.expression is not None:
                init_statement.expression.accept(self)
                currency = self.check_expression_currency(init_statement.expression)
                if currency is None:
                    raise CurrencyNotDefinedError(name)
                variable = CurrencyVariable(name, self.scope_manager.last_result.value, currency)
                self.scope_manager.add_variable(name, variable)
            else:
                self.scope_manager.add_variable(name, CurrencyVariable(name))
        else:
            raise InvalidVariableTypeError(name)

    # TODO test
    def visit_assign_statement(self, assign_statement):
        name = assign_statement.id
        assign_statement.expression.accept(self)
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

    # TODO test
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
        result = self.scope_manager.last_result.value
        for additive_op, multipl_expr in zip(expression.additive_ops, expression.multipl_exprs[1:]):
            multipl_expr.accept(self)
            if additive_op == TokenTypes.PLUS:
                result += self.scope_manager.last_result.value
            elif additive_op == TokenTypes.MINUS:
                result -= self.scope_manager.last_result.value
        self.scope_manager.last_result.value = result

    def visit_multipl_expr(self, multipl_expr):  # primaryExpr, { multiplOp, primaryExpr } ;
        multipl_expr.primary_exprs[0].accept(self)
        result = self.scope_manager.last_result.value
        for multipl_op, primary_expr in zip(multipl_expr.multipl_ops, multipl_expr.primary_exprs[1:]):
            primary_expr.accept(self)
            if multipl_op == TokenTypes.MULTIPLY:
                result *= self.scope_manager.last_result.value
            elif multipl_op == TokenTypes.DIVIDE:
                if self.scope_manager.last_result.value == 0:
                    raise DivisionZeroError
                result /= self.scope_manager.last_result.value
        self.scope_manager.last_result.value = result

    # TODO test, minus, currency
    def visit_primary_expr(self, primary_expr):  # [ “-” ], [currency | getCurrency], ( number | id |
        # parenthExpr | functionCall ), [currency | getCurrency] ;
        if primary_expr.number is not None:
            self.scope_manager.last_result = DecimalVariable('', primary_expr.number)
        elif primary_expr.id is not None:
            variable = self.scope_manager.get_variable(primary_expr.id)
            self.scope_manager.last_result = variable
        elif primary_expr.parenth_expr is not None:
            primary_expr.parenth_expr.accept(self)
        elif primary_expr.function_call is not None:
            primary_expr.function_call.accept(self)

    # TODO test
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
        equality_condition.relational_cond1.accept(self)
        if isinstance(self.scope_manager.last_result, bool):
            if self.scope_manager.last_result:
                result = True
        else:
            result = self.scope_manager.last_result
        if equality_condition.equal_op is not None:
            result = False
            equality_condition.relational_cond1.accept(self)
            result1 = self.scope_manager.last_result
            equality_condition.relational_cond2.accept(self)
            result2 = self.scope_manager.last_result  # TODO currency types
            if isinstance(result1, DecimalVariable) and isinstance(result2, DecimalVariable):
                if equality_condition.equal_op == TokenTypes.EQUAL:
                    if result1.value == result2.value:
                        result = True
                elif equality_condition.equal_op == TokenTypes.NOT_EQUAL:
                    if result1.value != result2.value:
                        result = True
        self.scope_manager.last_result = result

    def visit_relational_cond(self, relational_cond):  # primaryCond, [ relationOp, primaryCond ];
        result = False
        relational_cond.primary_cond1.accept(self)
        if isinstance(self.scope_manager.last_result, bool):
            if self.scope_manager.last_result:
                result = True
        else:
            result = self.scope_manager.last_result
        if relational_cond.relation_op is not None:
            result = False
            relational_cond.primary_cond1.accept(self)
            result1 = self.scope_manager.last_result
            relational_cond.primary_cond2.accept(self)
            result2 = self.scope_manager.last_result  # TODO currency
            if isinstance(result1, DecimalVariable) and isinstance(result2, DecimalVariable):
                if relational_cond.relation_op == TokenTypes.GREATER_THAN:
                    if result1.value > result2.value:
                        result = True
                elif relational_cond.relation_op == TokenTypes.LESS_THAN:
                    if result1.value < result2.value:
                        result = True
                elif relational_cond.relation_op == TokenTypes.GREATER_OR_EQUAL:
                    if result1.value >= result2.value:
                        result = True
                elif relational_cond.relation_op == TokenTypes.LESS_OR_EQUAL:
                    if result1.value <= result2.value:
                        result = True
        self.scope_manager.last_result = result

    # TODO test
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

    # TODO test
    def visit_parenth_cond(self, parenth_cond):
        parenth_cond.condition.accept(self)

    def visit_get_currency(self, get_currency):
        variable = self.scope_manager.get_variable(get_currency.id)
        if isinstance(variable, CurrencyVariable):
            self.scope_manager.last_result = variable.currency
        else:
            raise GetCurrencyError(get_currency.id)

    # TODO test
    def execute_function(self, function, arguments):
        check_arguments(function, arguments)
        self.scope_manager.create_new_scope_and_switch(function)
        self.add_arguments_to_function_scope(function, arguments)
        function.block.accept(self)
        check_returned_type(function, self.scope_manager.last_result)
        self.scope_manager.switch_to_parent_context()

    # TODO test
    def add_arguments_to_function_scope(self, function, arguments):
        for argument, parameter_signature in zip(arguments, function.parameters.signatures):
            self.scope_manager.current_scope.add_variable(parameter_signature.id, argument)

    # TODO test
    def check_expression_currency(self, expression):
        currency = None
        if expression is not None \
                and expression.multipl_exprs[0] is not None \
                and expression.multipl_exprs[0].primary_exprs[0] is not None \
                and expression.multipl_exprs[0].primary_exprs[0].currency1 is not None:
            currency = expression.multipl_exprs[0].primary_exprs[0].currency1
        if expression is not None \
                and expression.multipl_exprs[0] is not None \
                and expression.multipl_exprs[0].primary_exprs[0] is not None \
                and expression.multipl_exprs[0].primary_exprs[0].id is not None:
            _id = expression.multipl_exprs[0].primary_exprs[0].id
            variable = self.scope_manager.get_variable(_id)
            if isinstance(variable, CurrencyVariable):
                currency = variable.currency
        if expression is not None \
                and expression.multipl_exprs[0] is not None \
                and expression.multipl_exprs[0].primary_exprs[0] is not None \
                and expression.multipl_exprs[0].primary_exprs[0].currency2 is not None:
            currency = expression.multipl_exprs[0].primary_exprs[0].currency2
        return currency
