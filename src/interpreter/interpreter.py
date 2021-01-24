from .scope import ScopeManager
from ..parser.grammar import *
from .variables import *
from .utils import *
from ..lexer.token_types import TokenTypes
from ..exceptions.exceptions import MainNotDeclaredError, CurrencyNotDefinedError, InvalidVariableTypeError, \
    GetCurrencyError


class Interpreter:
    def __init__(self, program: Program):
        self.program = program
        self.scope_manager = ScopeManager()

    def interpret(self):
        self.program.accept(self)

    def visit_program(self, program: Program):
        main_declared = False
        for function_def in program.function_defs:
            if function_def.signature.id == "main":
                main_declared = True
                function_def.accept(self)
        if not main_declared:
            raise MainNotDeclaredError

    def visit_function_def(self, function_def: FunctionDef):
        self.scope_manager.add_function(function_def.signature.id, function_def)

    def visit_block(self, block: Block):
        for statement in block.statements:
            statement.accept(self)

    def visit_if_statement(self, if_statement: IfStatement):
        condition_result = if_statement.condition.accept(self)
        if condition_result:
            for statement in if_statement.block1.statements:
                statement.accept(self)
        else:
            for statement in if_statement.block2.statements:
                statement.accept(self)

    def visit_while_statement(self, while_statement: WhileStatement):
        condition_result = while_statement.condition.accept(self)
        while condition_result:
            for statement in while_statement.block.statements:
                statement.accept(self)
            condition_result = while_statement.condition.accept(self)

    def visit_return_statement(self, return_statement: ReturnStatement):
        return return_statement.expression.accept(self)

    def visit_init_statement(self, init_statement: InitStatement):  # signature, [ assignmentOp, expression ], “;” ;
        name = init_statement.signature.id
        if init_statement.signature.type == TokenTypes.DECIMAL:
            value = init_statement.expression.accept(self)
            variable = DecimalVariable(name, value)
            self.scope_manager.add_variable(name, variable)
        elif init_statement.signature.type == TokenTypes.CURRENCY:
            value = init_statement.expression.accept(self)
            currency = self.check_expression_currency(init_statement.expression)
            if currency is None:
                raise CurrencyNotDefinedError(name)
            variable = CurrencyVariable(name, value, currency)
            self.scope_manager.add_variable(name, variable)
        else:
            raise InvalidVariableTypeError(name)

    def visit_assign_statement(self, assign_statement: AssignStatement):
        name = assign_statement.id
        value = assign_statement.expression.accept(self)
        self.scope_manager.update_variable(name, value)

    def visit_print_statement(self, print_statement: PrintStatement):
        print_string = ''
        for printable in print_statement.printables:
            if isinstance(printable, str):
                print_string += printable
            else:
                result = printable.accept(self)
                print_string += str(result)
        print(print_string)

    def visit_function_call(self, function_call: FunctionCall):
        name = function_call.id
        function = self.scope_manager.get_function(name)
        arguments = [expression.accept(self) for expression in function_call.arguments.expressions]
        function_result = self.execute_function(function, arguments)
        return function_result

    def visit_expression(self, expression: Expression):
        pass

    def visit_condition(self, condition: Condition):
        pass

    def visit_get_currency(self, get_currency: GetCurrency):
        variable = self.scope_manager.get_variable(get_currency.id)
        if isinstance(variable, CurrencyVariable):
            return variable.currency
        raise GetCurrencyError(get_currency.id)

    def execute_function(self, function: FunctionDef, arguments):
        check_arguments(function, arguments)
        self.scope_manager.switch_context_to(function)
        self.add_arguments_to_function_scope(function, arguments)
        function_result = function.block.accept(self)
        check_returned_type(function, function_result)
        self.scope_manager.switch_to_parent_context()
        return function_result

    def add_arguments_to_function_scope(self, function: FunctionDef, arguments):
        for argument, parameter_signature in zip(arguments, function.parameters.signatures):
            self.scope_manager.current_scope.add_variable(parameter_signature.id, argument)

    def check_expression_currency(self, expression: Expression):
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
