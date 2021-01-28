from ..exceptions.exceptions import UndeclaredError, OverwriteError, VariableNotDeclaredError, NoParentContextError, \
    ChangeVariableTypeError, CurrencyNotDefinedOrChangeVariableTypeError
from .variables import *
from typing import Optional, Tuple


class Scope:
    def __init__(self, name: str, parent=None):
        self.name = name
        self.parent = parent
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
        self.global_scope = Scope("global")
        self.current_scope = Scope('main')
        self.last_result: Optional[CurrencyVariable, DecimalVariable, bool, str, Tuple, int, float] = None

    def add_variable(self, name, variable):
        if name in self.current_scope.symbols.keys():
            raise OverwriteError(name)
        self.current_scope.add_symbol(name, variable)

    def update_variable(self, name, variable):
        if name not in self.current_scope.symbols.keys():
            raise VariableNotDeclaredError(name)
        if isinstance(self.current_scope.symbols[name], CurrencyVariable) \
                and self.current_scope.symbols[name].currency is None \
                and isinstance(variable, DecimalVariable):
            raise CurrencyNotDefinedOrChangeVariableTypeError(name)
        if not isinstance(variable, type(self.current_scope.symbols[name])):
            raise ChangeVariableTypeError(name)
        self.current_scope.symbols[name] = variable

    def get_variable(self, name):
        return self.current_scope.get_symbol(name)

    def add_function(self, name, function):
        self.global_scope.add_symbol(name, function)

    def get_function(self, name):
        return self.global_scope.get_symbol(name)

    def create_new_scope_and_switch(self, function):
        function_scope = Scope(function.signature.id, self.current_scope)
        self.current_scope = function_scope

    def switch_to_parent_context(self):
        if not self.current_scope.parent:
            raise NoParentContextError(self.current_scope.name)
        self.current_scope = self.current_scope.parent
