from src.source.currencies_reader import CurrenciesReader
from src.source.currencies import Currencies
from src.lexer.tokens import Tokens
from src.lexer.token_types import TokenTypes
from src.lexer.lexer import Lexer
from src.parser.parser import Parser
from src.interpreter.interpreter import Interpreter
from src.source.source import FileSource
import sys


if __name__ == "__main__":
    program_file_path = sys.argv[1]
    program = open(program_file_path)

    currencies_file_path = sys.argv[2]
    CurrenciesReader(currencies_file_path)
    currencies = Currencies.currencies
    for currency in currencies:
        Tokens.keywords[currency] = TokenTypes.CURRENCY_TYPE

    lexer = Lexer(FileSource(program))
    parser = Parser(lexer)
    interpreter = Interpreter(parser)
    interpreter.interpret()

    program.close()
