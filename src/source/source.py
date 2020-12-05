class Source:
    def __init__(self, source_stream):
        self.source_stream = source_stream

    def get_next_char(self):
        pass

    def get_position(self):
        pass


class FileSource(Source):
    def __init__(self):
        self.line = 1
        self.column = 0
        self.character = self.get_next_char()

    def get_next_char(self):
        self.character = self.source_stream.read(1)
        if self.character == '/':
            self.character = self.source_stream.read(1)
            if self.character == '/':
                while self.character != '\n':
                    self.character = self.source_stream.read(1)
        if self.character == '\n':
            self.line += 1
            self.column = 0
        else:
            self.column += 1
        return self.character

    def get_position(self):
        return self.line, self.column
