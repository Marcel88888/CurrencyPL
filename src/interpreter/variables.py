from ..source.currencies_reader import CurrenciesReader


class CurrencyVariable:
    def __init__(self, name, value, currency):
        self.name = name
        self.value = value  # amount without currency
        self.currency = currency
        self.currency_value = self.value * self.currency.rate

    def calc_cur_val(self, currency=None, value=None):
        if currency is None and value is None:
            return
        if currency is not None:
            self.currency = currency
        if value is not None:
            self.value = value
        self.currency_value = self.value * self.currency.rate

    # TODO mathematical methods to calculate currency value


class DecimalVariable:
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def add(self, number):
        self.value += number

    def subtract(self, number):
        self.value -= number

    def multiply(self, number):
        self.value *= number

    def divide(self, number):
        self.value /= number
