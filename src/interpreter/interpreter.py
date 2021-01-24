from .scope import ScopeManager
from ..exceptions.exceptions import MainNotDeclaredError


class Interpreter:
    def __init__(self, program):
        self.program = program
        self.scope_manager = ScopeManager()

    def interpret(self):
        self.program.accept(self)

    def visit_program(self, program):
        main_declared = False
        for function_def in program.function_defs:
            if function_def.signature.id == "main":
                main_declared = True
        if not main_declared:
            raise MainNotDeclaredError
        for function_def in program.function_defs:
            function_def.accept(self)

    def visit_function_def(self, function_def):
        self.scope_manager.add_function(function_def.signature.id, function_def)

    def visit_block(self, block):
        for statement in block.statements:
            statement.accept(self)

    def visit_if_statement(self, if_statement):
        pass
        # if if_statement.condition:
        #     if_statement.block1.accept(self)
        # else:
        #     if_statement.block2.accept(self)

    def visit_while_statement(self, while_statement):
        pass
        # while while_statement.condition:
        #     while_statement.block.accept(self)

    def visit_return_statement(self, return_statement):
        pass
        # return return_statement.expression.accept(self)

    def visit_init_statement(self, init_statement):  # signature, [ assignmentOp, expression ], “;” ;
        pass
        # variable_name = init_statement.signature.id
        # variable_type = init_statement.signature.type

    def visit_assign_statement(self, assign_statement):
        pass

    def visit_print_statement(self, print_statement):
        pass

    def visit_function_call(self, function_call):
        pass

    def visit_expression(self, expression):
        pass
