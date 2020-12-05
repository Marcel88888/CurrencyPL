import json


class CurrenciesReader:
    def __init__(self, file_name):
        f = open(file_name)
        self.rates = json.load(f)
        self.currencies = []
        for key, value in self.rates.items():
            self.currencies.append(key)
