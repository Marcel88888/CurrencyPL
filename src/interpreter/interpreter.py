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
        if_statement.condition.accept(self)
        condition_result = self.scope_manager.last_result
        if condition_result:
            for statement in if_statement.block1.statements:
                statement.accept(self)
        else:
            for statement in if_statement.block2.statements:
                statement.accept(self)

    def visit_while_statement(self, while_statement: WhileStatement):
        while_statement.condition.accept(self)
        condition_result = self.scope_manager.last_result
        while condition_result:
            for statement in while_statement.block.statements:
                statement.accept(self)
            while_statement.condition.accept(self)
            condition_result = self.scope_manager.last_result

    def visit_return_statement(self, return_statement: ReturnStatement):
        return_statement.expression.accept(self)

    def visit_init_statement(self, init_statement: InitStatement):  # signature, [ assignmentOp, expression ], “;” ;
        name = init_statement.signature.id
        if init_statement.signature.type == TokenTypes.DECIMAL:
            init_statement.expression.accept(self)
            value = self.scope_manager.last_result
            variable = DecimalVariable(name, value)
            self.scope_manager.add_variable(name, variable)
        elif init_statement.signature.type == TokenTypes.CURRENCY:
            init_statement.expression.accept(self)
            value = self.scope_manager.last_result
            currency = self.check_expression_currency(init_statement.expression)
            if currency is None:
                raise CurrencyNotDefinedError(name)
            variable = CurrencyVariable(name, value, currency)
            self.scope_manager.add_variable(name, variable)
        else:
            raise InvalidVariableTypeError(name)

    def visit_assign_statement(self, assign_statement: AssignStatement):
        name = assign_statement.id
        assign_statement.expression.accept(self)
        value = self.scope_manager.last_result
        self.scope_manager.update_variable(name, value)

    def visit_print_statement(self, print_statement: PrintStatement):
        print_string = ''
        for printable in print_statement.printables:
            if isinstance(printable, str):
                print_string += printable
            else:
                printable.accept(self)
                result = self.scope_manager.last_result
                print_string += str(result)
        print(print_string)

    def visit_function_call(self, function_call: FunctionCall):
        name = function_call.id
        function = self.scope_manager.get_function(name)
        arguments = []
        for expression in function_call.arguments.expressions:
            expression.accept(self)
            arguments.append(self.scope_manager.last_result)
        self.execute_function(function, arguments)

    def visit_expression(self, expression: Expression):
        pass

    def visit_condition(self, condition: Condition):  # andCond, { orOp, andCond } ;
        for and_cond in condition.and_conds:
            and_cond.accept(self)
            if self.scope_manager.last_result:
                self.scope_manager.last_result = True
        self.scope_manager.last_result = False

    def visit_and_cond(self, and_cond: AndCond):  # equalityCond, { andOp, equalityCond } ;
        result = True
        for equality_cond in and_cond.equality_conds:
            equality_cond.accept(self)
            if not self.scope_manager.last_result:
                result = False
        self.scope_manager.last_result = result

    def visit_equality_cond(self, equality_condition: EqualityCond):  # relationalCond, [ equalOp, relationalCond ] ;
        result = False
        equality_condition.relational_cond1.accept(self)
        if self.scope_manager.last_result:
            result = True
        if equality_condition.equal_op is not None:
            result = False
            equality_condition.relational_cond1.accept(self)
            result1 = self.scope_manager.last_result
            equality_condition.relational_cond2.accept(self)
            result2 = self.scope_manager.last_result
            if equality_condition.equal_op == TokenTypes.EQUAL:
                if result1 == result2:
                    result = True
            elif equality_condition.equal_op == TokenTypes.NOT_EQUAL:
                if result1 != result2:
                    result = True
        self.scope_manager.last_result = result

    def visit_relational_cond(self, relational_cond: RelationalCond):  # primaryCond, [ relationOp, primaryCond ];
        result = False
        if relational_cond.primary_cond1.accept(self):
            result = True
        if relational_cond.relation_op is not None:
            result = False
            relational_cond.primary_cond1.accept(self)
            result1 = self.scope_manager.last_result
            relational_cond.primary_cond2.accept(self)
            result2 = self.scope_manager.last_result
            if relational_cond.relation_op == TokenTypes.GREATER_THAN:
                if result1 > result2:
                    result = True
            elif relational_cond.relation_op == TokenTypes.LESS_THAN:
                if result1 < result2:
                    result = True
            elif relational_cond.relation_op == TokenTypes.GREATER_OR_EQUAL:
                if result1 >= result2:
                    result = True
            elif relational_cond.relation_op == TokenTypes.LESS_OR_EQUAL:
                if result1 <= result2:
                    result = True
        self.scope_manager.last_result = result

    # def visit_primary_cond(self, primary_cond: PrimaryCond):  # [ unaryOp ], ( parenthCond | expression ) ;
    #     result = False
    #     if primary_cond.parenth_cond is not None:
    #         parenth_cond = primary_cond.parenth_cond.accept(self)
    #         if parenth_cond:
    #             result = True
    #     elif primary_cond.expression

    def visit_parenth_cond(self, parenth_cond: ParenthCond):
        pass

    def visit_get_currency(self, get_currency: GetCurrency):
        variable = self.scope_manager.get_variable(get_currency.id)
        if isinstance(variable, CurrencyVariable):
            self.scope_manager.last_result = variable.currency
        raise GetCurrencyError(get_currency.id)

    def execute_function(self, function: FunctionDef, arguments):
        check_arguments(function, arguments)
        self.scope_manager.switch_context_to(function)
        self.add_arguments_to_function_scope(function, arguments)
        function.block.accept(self)
        function_result = self.scope_manager.last_result
        check_returned_type(function, function_result)
        self.scope_manager.switch_to_parent_context()

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
