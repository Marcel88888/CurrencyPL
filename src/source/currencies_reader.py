import json
from currency import Currency


class CurrenciesReader:
    def __init__(self, file_name):
        file = open(file_name)
        self.rates = json.load(file)
        self.currencies = []
        for key, value in self.rates.items():
            currency = Currency(key, value)
            self.currencies.append(currency)
