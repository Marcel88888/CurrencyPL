class FunctionDef:  # signature, “(”, parameters, “)”, “{“, block, “}” ;
    def __init__(self, _type, _id, parameters, block):
        self.type = _type
        self.id = _id
        self.parameters = parameters
        self.block = block
