import sys
from src.source.currencies_reader import CurrenciesReader


if __name__ == "__main__":
    currencies_file_name = sys.argv[1]
    CurrenciesReader(currencies_file_name)

