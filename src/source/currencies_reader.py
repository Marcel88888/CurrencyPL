import json
from .currencies import Currencies


class CurrenciesReader:
    def __init__(self, file_path):
        with open(file_path, 'r') as file:
            Currencies.currencies = json.loads(file.read())
