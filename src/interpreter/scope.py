from ..exceptions.exceptions import UndeclaredError, OverwriteError


class Scope:
    def __init__(self, function_defs):
        self.function_defs = function_defs
        self.variables = {}

    def create_variable(self, name, value):
        if name not in self.variables.keys():
            self.variables[name] = value
        raise OverwriteError(OverwriteError.Types.VARIABLE.value, name)

    def get_variable_value(self, name):
        if name in self.variables.keys():
            return self.variables[name]
        raise UndeclaredError(UndeclaredError.Types.VARIABLE.value, name)


