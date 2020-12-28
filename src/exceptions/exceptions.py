class InvalidTokenError(Exception):
    def __init__(self, line, column):
        self.line = line
        self.column = column
        self.massage = f"Invalid token on position: {self.line}, {self.column}"
        super().__init__(self.massage)


class InvalidNumberTokenError(Exception):
    def __init__(self, line, column):
        self.line = line
        self.column = column
        self.massage = f"Invalid number token on position: {self.line}, {self.column}"
        super().__init__(self.massage)


class TokenTooLongError(Exception):
    def __init__(self, line, column):
        self.line = line
        self.column = column
        self.massage = f"Token too long on position: {self.line}, {self.column}"
        super().__init__(self.massage)


class StringTooLongError(Exception):
    def __init__(self, line, column):
        self.line = line
        self.column = column
        self.massage = f"Token too long on position: {self.line}, {self.column}"
        super().__init__(self.massage)


class _SyntaxError(Exception):
    def __init__(self, line, column):
        self.line = line
        self.column = column
        self.massage = f"Syntax error on position: {self.line}, {self.column}"
        super().__init__(self.massage)
