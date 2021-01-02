import sys
from src.source.currencies_reader import CurrenciesReader
from src.lexer.tokens import Tokens
from src.lexer.token_types import TokenTypes


if __name__ == "__main__":
    # currencies_file_name = sys.argv[1]
    # currencies_reader = CurrenciesReader(currencies_file_name)
    currencies_reader = CurrenciesReader("resources/currencies.json")
    currencies = currencies_reader.currencies
    for currency in currencies:
        Tokens.keywords[currency.name] = TokenTypes.CURRENCY_TYPE

