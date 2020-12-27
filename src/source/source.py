class Source:
    def __init__(self, source_stream):
        self.source_stream = source_stream

    def move_carr_one_pos(self):
        pass

    def get_position(self):
        pass


class FileSource(Source):
    def __init__(self, file_source):
        super(FileSource, self).__init__(file_source)
        self.line = 1
        self.column = 1
        self.byte_position = 1
        self.character = None

    def move_carr_one_pos(self):
        self.character = self.source_stream.read(1)
        self.byte_position += 1
        if self.character == '\n':
            self.line += 1
            self.column = 1
        else:
            self.column += 1

    def get_position(self):
        return self.line, self.column
