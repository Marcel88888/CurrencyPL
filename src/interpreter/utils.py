from ..exceptions.exceptions import InvalidReturnedTypeError, IncorrectArgumentsNumberError, InvalidArgumentTypeError
from ..parser.grammar import FunctionDef
from .variables import *
from ..lexer.token_types import TokenTypes


def check_returned_type(function: FunctionDef, function_result):
    if function.signature.type == TokenTypes.VOID and function_result is not None \
            or function.signature.type == TokenTypes.DECIMAL and not isinstance(function_result, DecimalVariable) \
            or function.signature.type == TokenTypes.CURRENCY and not isinstance(function_result, CurrencyVariable):
        raise InvalidReturnedTypeError(function.signature.type, type(function_result))


def check_arguments(function: FunctionDef, arguments):
    check_arguments_number(function, arguments)
    check_arguments_types(function, arguments)


def check_arguments_number(function: FunctionDef, arguments):
    if len(arguments) != len(function.parameters.signatures):
        raise IncorrectArgumentsNumberError(function.signature.id, len(function.parameters.signatures), len(arguments))


def check_arguments_types(function: FunctionDef, arguments):
    for argument, parameter_signature in zip(arguments, function.parameters.signatures):
        if parameter_signature.type == TokenTypes.DECIMAL and not isinstance(argument, DecimalVariable) \
                or parameter_signature.type == TokenTypes.CURRENCY and not isinstance(argument, CurrencyVariable):
            raise InvalidArgumentTypeError(function.signature.id, parameter_signature.id)
