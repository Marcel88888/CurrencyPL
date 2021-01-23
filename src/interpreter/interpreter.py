from .scope import Scope


class Interpreter:
    def __init__(self, program):
        self.program = program
        self.scope = Scope()

    def interpret(self):
        # for function_def in program.function_defs:
        #     function_def.accept(self)
        self.program.accept(self)

    def visit_function_def(self, function_def):
        if function_def.block is not None:
            return function_def.block.accept(self)

    def visit_block(self, block):
        for statement in block.statements:
            statement.accept(self)

    def visit_if_statement(self, if_statement):
        if if_statement.condition:
            if_statement.block1.accept(self)
        else:
            if_statement.block2.accept(self)

    def visit_while_statement(self, while_statement):
        while while_statement.condition:
            while_statement.block.accept(self)

    def visit_return_statement(self, return_statement):
        return return_statement.expression.accept(self)

    def visit_init_statement(self, init_statement):  # signature, [ assignmentOp, expression ], “;” ;
        variable_name = init_statement.signature.id
        variable_type = init_statement.signature.type

    def visit_assign_statement(self, assign_statement):
        pass

    def visit_print_statement(self, print_statement):
        pass

    def visit_function_call(self, function_call):
        pass

    def visit_expression(self, expression):
        pass
