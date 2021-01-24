from ..exceptions.exceptions import UndeclaredError


class Scope:
    def __init__(self):
        self.symbols = {}

    def add_or_update_symbol(self, name, value):
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

    def add_or_update_variable(self, name, value):
        self.current_scope.add_or_update_symbol(name, value)

    def get_variable(self, name):
        return self.current_scope.get_symbol(name)

    def add_function(self, name, function):
        self.global_scope.add_or_update_symbol(name, function)

    def get_function(self, name):
        self.global_scope.get_symbol(name)
