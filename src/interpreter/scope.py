from ..exceptions.exceptions import UndeclaredError, OverwriteError, VariableNotDeclared


class Scope:
    def __init__(self):
        self.symbols = {}

    def add_symbol(self, name, value):
        self.symbols[name] = value

    def get_symbol(self, name):
        symbol = self.symbols[name]
        if symbol is None:
            raise UndeclaredError(name)
        return symbol

    def copy_symbols_from(self, source):
        self.symbols.update(source)


class ScopeManager:
    def __init__(self):
        self.global_scope = Scope()
        self.current_scope = Scope()

    def add_variable(self, name, variable):
        if name in self.current_scope.symbols.keys():
            raise OverwriteError(name)
        self.current_scope.add_symbol(name, variable)

    def update_variable(self, name, value):
        if name not in self.current_scope.symbols.keys():
            raise VariableNotDeclared(name)
        self.current_scope.symbols[name].value = value

    def get_variable(self, name):
        return self.current_scope.get_symbol(name)

    def add_function(self, name, function):
        self.global_scope.add_or_update_symbol(name, function)

    def get_function(self, name):
        self.global_scope.get_symbol(name)
