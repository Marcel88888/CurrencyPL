from .token_types import TokenTypes


class Tokens:
    keywords = {
        'if': TokenTypes.IF,
        'else': TokenTypes.ELSE,
        'while': TokenTypes.WHILE,
        'return': TokenTypes.RETURN,
        'dec': TokenTypes.DECIMAL,
        'cur': TokenTypes.CURRENCY,
        'print': TokenTypes.PRINT,
        'getCurrency': TokenTypes.GET_CURRENCY
    }

    single_symbols = {
        '(': TokenTypes.OP_BRACKET,
        ')': TokenTypes.CL_BRACKET,
        '{': TokenTypes.OP_CURLY_BRACKET,
        '}': TokenTypes.CL_CURLY_BRACKET,
        '[': TokenTypes.OP_SQUARE_BRACKET,
        ']': TokenTypes.CL_SQUARE_BRACKET,
        '+': TokenTypes.PLUS,
        '-': TokenTypes.MINUS,
        '*': TokenTypes.MULTIPLY,
        '/': TokenTypes.DIVIDE,
        '=': TokenTypes.ASSIGNMENT,
        '>': TokenTypes.GREATER_THAN,
        '<': TokenTypes.LESS_THAN,
        ',': TokenTypes.COMMA,
        ';': TokenTypes.SEMICOLON,
        '.': TokenTypes.DOT,
        '!': TokenTypes.NOT,
        '&': TokenTypes.AND,
        '|': TokenTypes.OR
    }

    double_symbols = {
        '==': TokenTypes.EQUAL,
        '!=': TokenTypes.NOT_EQUAL,
        '>=': TokenTypes.GREATER_OR_EQUAL,
        '<=': TokenTypes.LESS_OR_EQUAL
    }


