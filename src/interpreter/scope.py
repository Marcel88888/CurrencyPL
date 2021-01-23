class Scope:
    def __init__(self):
        self.stack = []

    def pop_function_scope(self):
        self.stack.pop()

    def add_function_scope(self):
        self.stack.append(FunctionScope())

    def add_or_update_variable(self, name, variable):
        self.stack[-1].variables[name] = variable

    def get_variable(self, name):
        return self.stack[-1].variables[name]

    def variable_exists(self, name):
        return name in self.stack[-1].variables.keys()

    def add_argument(self, variable):
        self.stack[-1].arguments.push(variable)

    def get_argument(self, number):
        return self.stack[-1].arguments[number]

    def remove_all_arguments(self):
        self.stack[-1].arguments = []

    def get_arguments_number(self):
        return len(self.stack[-1].arguments)

    def set_returned_value(self, variable):
        self.stack[-1].returned_value = variable

    def get_returned_value(self):
        return self.stack[-1].returned_value


class FunctionScope:
    def __init__(self):
        self.variables = {}
        self.arguments = []
        self.returned_value = None
