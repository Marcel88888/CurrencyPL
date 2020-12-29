class FunctionDef:  # signature, “(”, parameters, “)”, “{“, block, “}” ;
    def __init__(self, signature, parameters, block):
        self.signature = signature
        self.parameters = parameters
        self.block = block


class Signature:
    def __init__(self, _type, _id):
        self.type = _type
        self.id = _id
