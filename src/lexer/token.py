from .token_types import TokenTypes
from ..numbers.currency_value import CurrencyValue


class Token:
    def __init__(self, _type, value, line, column):
        self.type = _type
        self.value = value
        self.numerical_value = None
        self.line = line
        self.column = column
        self.set_numerical_value()

    def __repr__(self):
        return f"token_type: {self.type}\n" \
               f"value: {self.value}\n" \
               f"position: {self.line}, {self.column}"

    def set_numerical_value(self):
        if self.type == TokenTypes.NUMBER:
            self.numerical_value = CurrencyValue(self.value)
