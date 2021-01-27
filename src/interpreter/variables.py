from typing import Union
from ..source.currencies_reader import CurrenciesReader


# TODO tests for exceptions

class CurrencyVariable:
    def __init__(self, name: str, value: Union[int, float] = None, currency: str = None):
        self.name = name
        self.value = value  # amount without currency
        self.currency = currency

    def exchange(self, new_currency: str):
        rate = CurrenciesReader.c


    # TODO mathematical methods to calculate currency value


class DecimalVariable:
    def __init__(self, name: str, value: Union[int, float] = None):
        self.name = name
        self.value = value

