class Interpreter:
    def __init__(self, parser, visitor):
        self.__parser = parser
        self.__visitor = visitor

    def interpret(self):
        self.__parser.parse_program()
        program = self.__parser.program
        for function_def in program.function_defs:
            function_def.accept(self.__visitor)