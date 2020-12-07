class Source:
    def __init__(self, source_stream):
        self.source_stream = source_stream

    def get_next_char(self):
        pass

    def get_position(self):
        pass


class FileSource(Source):
    def __init__(self, file_source):
        super(FileSource, self).__init__(file_source)
        self.line = 1
        self.column = 1
        self.character = None

    def get_next_char(self):
        self.character = self.source_stream.read(1)
        print(self.character)
        if self.character == '\n':
            print("AAAAAAAAAAAAAAAAAAAA")
            self.line += 1
            self.column = 1
            print(self.line)
        else:
            # print("BBBBBBBBBBBBBBB")
            self.column += 1
            print(self.line)
        return self.character

    def get_position(self):
        return self.line, self.column
