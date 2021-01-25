import json


class CurrenciesReader:
    def __init__(self, file_name):
        file = open(file_name)
        self.rates = json.load(file)
        self.currencies = {}
        for key, value in self.rates.items():
            self.currencies[key] = value
