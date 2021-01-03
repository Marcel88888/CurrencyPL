from .token_types import TokenTypes


class Token:
    def __init__(self, _type, line, column, value=None):
        self.line = line
        self.column = column
        self.type = _type
        self.value = value
        self.numerical_value = None
        self.set_numerical_value()

    def set_numerical_value(self):
        if self.type == TokenTypes.NUMBER:
            # self.numerical_value = CurrencyValue(self.value)
            self.numerical_value = float(self.value)
