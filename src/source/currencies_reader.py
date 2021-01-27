import json
from .currencies import Currencies


class CurrenciesReader:
    def __init__(self, file_name):
        file = open(file_name)
        Currencies.currencies = json.load(file)
