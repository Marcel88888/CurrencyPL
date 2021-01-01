class FunctionDef:  # signature, “(”, parameters, “)”, “{“, block, “}” ;
    def __init__(self, signature, parameters, block):
        self.signature = signature
        self.parameters = parameters
        self.block = block


class FunctionCall:  # id, “(“, arguments, “)”, “;” ;
    def __init__(self, _id, arguments):
        self.id = _id
        self.arguments = arguments


class Signature:  # type, id ;
    def __init__(self, _type, _id):
        self.type = _type
        self.id = _id


class Parameters:  # [ signature, { “,”, signature } ];
    def __init__(self, signatures):
        self.signatures = signatures


class Arguments:  # [ expression { “,”, expression } ] ;
    def __init__(self, expressions):
        self.expressions = expressions


class Block:  # { statement };
    def __init__(self, statements):
        self.statements = statements


class IfStatement:  # “if”, “(”, condition, “)”, “{“, block, “}“ ;
    def __init__(self, condition, block):
        self.condition = condition
        self.block = block


class WhileStatement:  # “while”, “(“, condition, “)”, “{“, block, “}“ ;
    def __init__(self, condition, block):
        self.condition = condition
        self.block = block


class ReturnStatement:  # “return”, expression, “;” ;
    def __init__(self, expression):
        self.expression = expression


class InitStatement:  # signature, [ assignmentOp, expression ], “;” ;
    def __init__(self, signature, expression=None):
        self.signature = signature
        self.expression = expression


class AssignStatement:  # id, assignmentOp, expression, “;” ;
    def __init__(self, _id, expression):
        self.id = _id
        self.expression = expression


class Condition:  # andCond, { orOp, andCond } ;
    def __init__(self, and_conds):
        self.and_conds = and_conds


class AndCond:  # equalityCond, { andOp, equalityCond } ;
    def __init__(self, equality_conds):
        self.equality_conds = equality_conds


class EqualityCond:  # relationalCond, [ equalOp, relationalCond ] ;
    def __init__(self, relational_conds):
        self.relational_conds = relational_conds


class RelationalCond:  # primaryCond, [ relationOp, primaryCond ];
    def __init__(self, primary_conds):
        self.primary_conds = primary_conds


class PrimaryCond:  # [ unaryOp ], ( parenthCond | expression ) ;
    def __init__(self, unary_op=False, parenth_cond=None, expression=None):
        self.unary_op = unary_op
        self.parenth_cond = parenth_cond
        self.expression = expression


class ParenthCond:  # “(“, condition, “)” ;
    def __init__(self, condition):
        self.condition = condition


class Expression:  # multiplExpr, { additiveOp, multiplExpr } ;
    def __init__(self, multipl_exprs):
        self.multipl_exprs = multipl_exprs


class MultiplExpr:  # primaryExpr, { multiplOp, primaryExpr } ;
    def __init__(self, primary_exprs):
        self.primary_exprs = primary_exprs


class PrimaryExpr:  # [ “-” ], [currency | getCurrency], ( number | id | parenthExpr | functionCall ),
    # [currency | getCurrency] ;
    def __init__(self, minus=False, currency=None, get_currency=None, number=None, _id=None, parenth_expr=None,
                 function_call=None):
        self.minus = minus
        self.currency = currency
        self.get_currency = get_currency
        self.number = number
        self.id = _id
        self.parenth_expr = parenth_expr
        self.function_call = function_call


class ParenthExpr:  # “(”, expression, “)” ;
    def __init__(self, expression):
        self.expression = expression


class GetCurrency:  # id, “.”, “getCurrency()” ;
    def __init__(self, _id):
        self.id = _id


class String:  # “””, { ( anyVisibleChar - “”” ) | “ ” }, “”” ;
    def __init__(self, string):
        self.string = string
