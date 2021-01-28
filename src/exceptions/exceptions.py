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


class SyntaxxError(Exception):
    def __init__(self, line, column):
        self.__line = line
        self.__column = column
        self.__message = f"Syntax error on position: {self.__line}, {self.__column}"
        super().__init__(self.__message)


class MainNotDeclaredError(Exception):
    def __init__(self):
        self.__message = "There is no 'main' function in the program."
        super().__init__(self.__message)


class OverwriteError(Exception):
    def __init__(self, name):
        self.__name = name
        self.__message = f"Variable ('{self.__name}') was already declared."
        super().__init__(self.__message)


class UndeclaredError(Exception):
    def __init__(self, name):
        self.__name = name
        self.__message = f"Variable '{self.__name}' not declared."
        super().__init__(self.__message)


class CurrencyNotDefinedError(Exception):
    def __init__(self, name):
        self.__name = name
        self.__message = f"Currency not declared for currency type variable named '{self.__name}'"
        super().__init__(self.__message)


class InvalidVariableTypeError(Exception):
    def __init__(self, name):
        self.__name = name
        self.__message = f"Invalid variable type for: '{self.__name}'"
        super().__init__(self.__message)


class InvalidReturnedTypeError(Exception):
    def __init__(self, function_returned_type, result_type):
        self.__function_returned_type = function_returned_type
        self.__result_type = result_type
        self.__message = f"Expected return type: {self.__function_returned_type}, got: {self.__result_type}"
        super().__init__(self.__message)


class NoParentContextError(Exception):
    def __init__(self, name):
        self.__name = name
        self.__message = f"No parent context for context: '{self.__name}'"
        super().__init__(self.__message)


class IncorrectArgumentsNumberError(Exception):
    def __init__(self, function_name: str, required_number: int, actual_number: int):
        self.__function_name = function_name
        self.__required_number = required_number
        self.__actual_number = actual_number
        self.__message = f"Incorrect arguments number for function: '{self.__function_name}'. Required: " \
                         f"{self.__required_number}, got: {self.__actual_number}"
        super().__init__(self.__message)


class InvalidArgumentTypeError(Exception):
    def __init__(self, function_name, parameter_name):
        self.__function_name = function_name
        self.__parameter_name = parameter_name
        self.__message = f"Invalid argument ('{self.__parameter_name}') type for function '{self.__function_name}'"
        super().__init__(self.__message)


class GetCurrencyError(Exception):
    def __init__(self, variable_name):
        self.__variable_name = variable_name
        self.__message = f"Attempt to call 'get_variable()' on the variable of a type other than the currency type " \
                         f"('{self.__variable_name}')"
        super().__init__(self.__message)


class DivisionZeroError(Exception):
    def __init__(self):
        self.__message = "Attempt to divide by zero"
        super().__init__(self.__message)


class CurrencyUsedForDecimalVariableError(Exception):
    def __init__(self):
        self.__message = "Currency used for decimal variable"
        super().__init__(self.__message)


class ChangeVariableTypeError(Exception):
    def __init__(self, variable_name):
        self.__variable_name = variable_name
        self.__message = f"Attempt to change variable ('{self.__variable_name}') type"
        super().__init__(self.__message)


class CurrencyNotDefinedOrChangeVariableTypeError(Exception):
    def __init__(self, name):
        self.__name = name
        self.__message = f"Variable ('{self.__name}') is already CurrencyVariable type. Attempt to change its type or" \
                         f"currency is not defined.)"
        super().__init__(self.__message)


class IllicitOperationError(Exception):
    def __init__(self):
        self.__message = "Illicit operation"
        super().__init__(self.__message)
