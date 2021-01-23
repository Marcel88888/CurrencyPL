from enum import Enum


class InvalidTokenError(Exception):
    def __init__(self, line, column):
        self.__line = line
        self.__column = column
        self.__message = f"Invalid token on position: {self.__line}, {self.__column}"
        super().__init__(self.__message)


class InvalidNumberTokenError(Exception):
    def __init__(self, line, column):
        self.__line = line
        self.__column = column
        self.__message = f"Invalid number token on position: {self.__line}, {self.__column}"
        super().__init__(self.__message)


class TokenTooLongError(Exception):
    def __init__(self, line, column):
        self.__line = line
        self.__column = column
        self.__message = f"Token too long on position: {self.__line}, {self.__column}"
        super().__init__(self.__message)


class StringTooLongError(Exception):
    def __init__(self, line, column):
        self.__line = line
        self.__column = column
        self.__message = f"Token too long on position: {self.__line}, {self.__column}"
        super().__init__(self.__message)


class _SyntaxError(Exception):
    def __init__(self, line, column):
        self.__line = line
        self.__column = column
        self.__message = f"Syntax error on position: {self.__line}, {self.__column}"
        super().__init__(self.__message)


class InterpretationError(Exception):
    class Types(Enum):
        VARIABLE = "variable"


class UndeclaredError(InterpretationError):
    def __init__(self, _type, name):
        self.__type = _type
        self.__name = name
        self.__message = f"Error: Undeclared {self.__type} named {self.__name}"
        super().__init__(self.__message)


class OverwriteError(InterpretationError):
    def __init__(self, _type, name):
        self.__type = _type
        self.__name = name
        self.__message = f"Error: Attempt to overwrite {self.__type} named {self.__name}"
        super().__init__(self.__message)

