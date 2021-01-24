from typing import List, Union
from ..lexer.token_types import TokenTypes
from ..interpreter.interpreter import Interpreter


class Node:
    def accept(self, visitor: Interpreter):
        pass


class Signature:  # type, id ;
    def __init__(self, _type, _id):
        self.type = _type
        self.id = _id


class Parameters:  # [ signature, { “,”, signature } ];
    def __init__(self, signatures: List[Signature]):
        self.signatures = signatures


class Arguments:  # [ expression { “,”, expression } ] ;
    def __init__(self, expressions):
        self.expressions = expressions


class Block:  # { statement };
    def __init__(self, statements):
        self.statements = statements

    def accept(self, visitor: Interpreter):
        visitor.visit_block(self)


class FunctionDef(Node):  # signature, “(”, parameters, “)”, “{“, block, “}” ;
    def __init__(self, signature: Signature, parameters: Parameters, block: Block):
        self.signature = signature
        self.parameters = parameters
        self.block = block

    def accept(self, visitor: Interpreter):
        visitor.visit_function_def(self)


class Program(Node):
    def __init__(self, function_defs: List[FunctionDef]):
        self.function_defs = function_defs

    def accept(self, visitor: Interpreter):
        visitor.visit_program(self)


class FunctionCall(Node):  # id, “(“, arguments, “)”;
    def __init__(self, _id: str, arguments: Arguments):
        self.id = _id
        self.arguments = arguments

    def accept(self, visitor: Interpreter):
        visitor.visit_function_call(self)


class GetCurrency(Node):  # id, “.”, “getCurrency()” ;
    def __init__(self, _id: str):
        self.id = _id

    def accept(self, visitor: Interpreter):
        visitor.visit_get_currency(self)


class ParenthExpr(Node):  # “(”, expression, “)” ;
    def __init__(self, expression):
        self.expression = expression

    def accept(self, visitor: Interpreter):
        visitor.visit_parenth_expr(self)


class PrimaryExpr(Node):  # [ “-” ], [currency | getCurrency], ( number | id | parenthExpr | functionCall ),
    # [currency | getCurrency] ;
    def __init__(self, minus: bool = False, currency1: str = None, get_currency1: GetCurrency = None,
                 number: Union[int, float] = None, _id: str = None, parenth_expr: ParenthExpr = None,
                 function_call: FunctionCall = None, currency2: str = None, get_currency2: GetCurrency = None):
        self.minus = minus
        self.currency1 = currency1
        self.get_currency1 = get_currency1
        self.number = number
        self.id = _id
        self.parenth_expr = parenth_expr
        self.function_call = function_call
        self.currency2 = currency2
        self.get_currency2 = get_currency2

    def accept(self, visitor: Interpreter):
        visitor.visit_primary_expr(self)


class MultiplExpr(Node):  # primaryExpr, { multiplOp, primaryExpr } ;
    def __init__(self, primary_exprs: List[PrimaryExpr], multipl_ops: List[Union[TokenTypes.MULTIPLY,
                                                                                 TokenTypes.DIVIDE]]):
        self.primary_exprs = primary_exprs
        self.multipl_ops = multipl_ops

    def accept(self, visitor: Interpreter):
        visitor.visit_multipl_expr(self)


class Expression(Node):  # multiplExpr, { additiveOp, multiplExpr } ;
    def __init__(self, multipl_exprs: List[MultiplExpr], additive_ops: Union[TokenTypes.PLUS, TokenTypes.MINUS]):
        self.multipl_exprs = multipl_exprs
        self.additive_ops = additive_ops

    def accept(self, visitor: Interpreter):
        visitor.visit_expression(self)


class ParenthCond(Node):  # “(“, condition, “)” ;
    def __init__(self, condition):
        self.condition = condition

    def accept(self, visitor: Interpreter):
        visitor.visit_parenth_cond(self)


class PrimaryCond(Node):  # [ unaryOp ], ( parenthCond | expression ) ;
    def __init__(self, unary_op: bool = False, parenth_cond: ParenthCond = None, expression: Expression = None):
        self.unary_op = unary_op
        self.parenth_cond = parenth_cond
        self.expression = expression

    def accept(self, visitor: Interpreter):
        visitor.visit_primary_cond(self)


class RelationalCond(Node):  # primaryCond, [ relationOp, primaryCond ];
    def __init__(self, primary_cond1: PrimaryCond, relation_op: Union[TokenTypes.GREATER_THAN,
                                                                      TokenTypes.LESS_THAN,
                                                                      TokenTypes.GREATER_OR_EQUAL,
                                                                      TokenTypes.LESS_OR_EQUAL] = None,
                 primary_cond2: PrimaryCond = None):
        self.primary_cond1 = primary_cond1
        self.relation_op = relation_op
        self.primary_cond2 = primary_cond2

    def accept(self, visitor: Interpreter):
        visitor.visit_relational_cond(self)


class EqualityCond(Node):  # relationalCond, [ equalOp, relationalCond ] ;
    def __init__(self, relational_cond1: RelationalCond, equal_op: Union[TokenTypes.EQUAL, TokenTypes.NOT_EQUAL] = None,
                 relational_cond2: RelationalCond = None):
        self.relational_cond1 = relational_cond1
        self.equal_op = equal_op
        self.relational_cond2 = relational_cond2

    def accept(self, visitor: Interpreter):
        visitor.visit_equality_cond(self)


class AndCond(Node):  # equalityCond, { andOp, equalityCond } ;
    def __init__(self, equality_conds: List[EqualityCond]):
        self.equality_conds = equality_conds

    def accept(self, visitor: Interpreter):
        visitor.visit_and_cond(self)


class Condition(Node):  # andCond, { orOp, andCond } ;
    def __init__(self, and_conds: List[AndCond]):
        self.and_conds = and_conds

    def accept(self, visitor: Interpreter):
        visitor.visit_condition(self)


class IfStatement:  # “if”, “(”, condition, “)”, “{“, block, “}“, [“else”, “{”, block, “}” ];
    def __init__(self, condition: Condition, block1: Block, block2: Block = None):
        self.condition = condition
        self.block1 = block1
        self.block2 = block2

    def accept(self, visitor: Interpreter):
        visitor.visit_if_statement(self)


class WhileStatement:  # “while”, “(“, condition, “)”, “{“, block, “}“ ;
    def __init__(self, condition: Condition, block: Block):
        self.condition = condition
        self.block = block

    def accept(self, visitor: Interpreter):
        visitor.visit_while_statement(self)


class ReturnStatement:  # “return”, expression, “;” ;
    def __init__(self, expression: Expression):
        self.expression = expression

    def accept(self, visitor: Interpreter):
        visitor.visit_return_statement(self)


class InitStatement:  # signature, [ assignmentOp, expression ], “;” ;
    def __init__(self, signature: Signature, expression: Expression = None):
        self.signature = signature
        self.expression = expression

    def accept(self, visitor: Interpreter):
        visitor.visit_init_statement(self)


class AssignStatement:  # id, assignmentOp, expression, “;” ;
    def __init__(self, _id: str, expression: Expression):
        self.id = _id
        self.expression = expression

    def accept(self, visitor: Interpreter):
        visitor.visit_assign_statement(self)


class PrintStatement:  # “print”, “(“, printable { “,”, printable }, “)”, ";" ;
    def __init__(self, printables: List[Union[str, Expression]]):
        self.printables = printables

    def accept(self, visitor: Interpreter):
        visitor.visit_print_statement(self)
