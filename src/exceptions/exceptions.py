class InvalidTokenError(Exception):
    def __init__(self, line, column):
        self.line = line
        self.column = column
        self.massage = "Invalid token on position: {self.line}, {self.column}"
        super().__init__(self.massage)
