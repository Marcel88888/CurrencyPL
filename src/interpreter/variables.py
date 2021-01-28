from typing import Union
from ..source.currencies import Currencies


class CurrencyVariable:
    def __init__(self, name: str, value: Union[int, float] = None, currency: str = None):
        self.name = name
        self.value = value  # amount without currency
        self.currency = currency

    def exchange(self, new_currency: str):
        if self.currency == new_currency:
            return
        rate = Currencies.currencies[self.currency][new_currency]
        self.value *= rate
        self.currency = new_currency


class DecimalVariable:
    def __init__(self, name: str, value: Union[int, float] = None):
        self.name = name
        self.value = value

