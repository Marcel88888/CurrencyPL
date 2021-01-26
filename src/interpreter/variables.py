from typing import Union
from ..source.currencies_reader import CurrenciesReader


# TODO tests for exceptions

class CurrencyVariable:
    def __init__(self, name: str, value: Union[int, float] = None, currency: str = None):
        self.name = name
        self.value = value  # amount without currency
        self.currency = currency
        # self.currency_value = self.value * self.currency.rate

    def calc_cur_val(self, currency=None, value: Union[int, float] = None):
        if currency is None and value is None:
            return
        if currency is not None:
            self.currency = currency
        if value is not None:
            self.value = value
        self.currency_value = self.value * self.currency.rate

    # TODO mathematical methods to calculate currency value


class DecimalVariable:
    def __init__(self, name: str, value: Union[int, float] = None):
        self.name = name
        self.value = value

    def add(self, number):
        self.value += number.value

    def subtract(self, number):
        self.value -= number.value

    def multiply(self, number):
        self.value *= number.value

    def divide(self, number):
        self.value /= number.value
