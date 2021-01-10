import io
import pytest
from ..src.lexer.lexer import Lexer
from ..src.lexer.token import TokenTypes
from ..src.lexer.tokens import Tokens
from ..src.source.currencies_reader import CurrenciesReader
from ..src.source.source import FileSource
from ..src.parser.parser import Parser
from ..src.parser.grammar import *
from ..src.exceptions.exceptions import _SyntaxError


def create_parser(source_string):
    currencies_reader = CurrenciesReader("resources/currencies.json")
    currencies = currencies_reader.currencies
    for currency in currencies:
        Tokens.keywords[currency.name] = TokenTypes.CURRENCY_TYPE
    lexer = Lexer(FileSource(io.StringIO(source_string)))
    return Parser(lexer)


def test_program():
    parser = create_parser('void main() {'
                           'dec a = 2;'
                           'dec b = 3;'
                           'dec result = add(a, b);'
                           'print(result);'
                           '}'
                           ''
                           'dec add(dec x, dec y) {'
                           'return x + y;'
                           '}')
    parser.parse_program()
    assert parser.program is not None
    assert len(parser.program.function_defs) == 2
    assert parser.program.function_defs[0].signature.type == TokenTypes.VOID
    assert parser.program.function_defs[0].signature.id == 'main'
    assert parser.program.function_defs[1].signature.type == TokenTypes.DECIMAL
    assert parser.program.function_defs[1].signature.id == 'add'


def test_function_def():  # signature, “(”, parameters, “)”, “{“, block, “}” ;
    parser = create_parser('dec check(dec a, dec b) {'
                           'dec c = a + b;'
                           'if (c > 0) {'
                           'print ("greater than 0");'
                           '}'
                           'return c;'
                           '}')
    function_def = parser.parse_function_def()
    assert function_def is not None
    assert function_def.signature.type == TokenTypes.DECIMAL
    assert function_def.signature.id == 'check'
    assert function_def.parameters.signatures[0].type == TokenTypes.DECIMAL
    assert function_def.parameters.signatures[0].id == 'a'
    assert function_def.parameters.signatures[1].type == TokenTypes.DECIMAL
    assert function_def.parameters.signatures[1].id == 'b'
    assert function_def.block.statements[0].signature.id == 'c'
    assert function_def.block.statements[0].expression.multipl_exprs[0].primary_exprs[0].id == 'a'
    assert function_def.block.statements[0].expression.additive_op == TokenTypes.PLUS
    assert function_def.block.statements[0].expression.multipl_exprs[1].primary_exprs[0].id == 'b'
    assert isinstance(function_def.block.statements[1], IfStatement)
    assert function_def.block.statements[1].condition.and_conds[0].equality_conds[
               0].relational_cond1.primary_cond1.expression.multipl_exprs[0].primary_exprs[0].id == 'c'
    assert function_def.block.statements[1].condition.and_conds[0].equality_conds[0].relational_cond1.relation_op == \
           TokenTypes.GREATER_THAN
    assert function_def.block.statements[1].condition.and_conds[0].equality_conds[
               0].relational_cond1.primary_cond2.expression.multipl_exprs[0].primary_exprs[0].number == 0
    assert isinstance(function_def.block.statements[1].block.statements[0], PrintStatement)
    assert function_def.block.statements[1].block.statements[0].printables == ['"greater than 0"']
    assert isinstance(function_def.block.statements[2], ReturnStatement)
    assert function_def.block.statements[2].expression.multipl_exprs[0].primary_exprs[0].id == 'c'


def test_signature():
    parser = create_parser("dec var")
    signature = parser.parse_signature()
    assert signature.type == TokenTypes.DECIMAL
    assert signature.id == 'var'


def test_signature_without_type():
    parser = create_parser("var")
    assert parser.parse_signature() is None


def test_parameters():
    parser = create_parser("dec a, cur b, dec var")
    parameters = parser.parse_parameters()
    assert parameters.signatures[0].type == TokenTypes.DECIMAL
    assert parameters.signatures[0].id == 'a'
    assert parameters.signatures[1].type == TokenTypes.CURRENCY
    assert parameters.signatures[1].id == 'b'
    assert parameters.signatures[2].type == TokenTypes.DECIMAL
    assert parameters.signatures[2].id == 'var'


def test_incorrect_parameters():
    parser = create_parser("dec a, b")
    with pytest.raises(_SyntaxError):
        parser.parse_parameters()


def test_empty_parameters():
    parser = create_parser(" ")
    parameters = parser.parse_parameters()
    assert not parameters.signatures


def test_arguments():  # [ expression { “,”, expression } ] ;
    parser = create_parser("a-b, c/d, e")
    arguments = parser.parse_arguments()
    assert arguments is not None
    assert arguments.expressions[0].multipl_exprs[0].primary_exprs[0].id == 'a'
    assert arguments.expressions[0].additive_op == TokenTypes.MINUS
    assert arguments.expressions[0].multipl_exprs[1].primary_exprs[0].id == 'b'
    assert arguments.expressions[1].multipl_exprs[0].primary_exprs[0].id == 'c'
    assert arguments.expressions[1].multipl_exprs[0].multipl_op == TokenTypes.DIVIDE
    assert arguments.expressions[1].multipl_exprs[0].primary_exprs[1].id == 'd'
    assert arguments.expressions[2].multipl_exprs[0].primary_exprs[0].id == 'e'


def test_arguments2():  # [ expression { “,”, expression } ] ;
    parser = create_parser("a-b, c/d, calculate(e, f)")
    arguments = parser.parse_arguments()
    assert arguments is not None
    assert arguments.expressions[0].multipl_exprs[0].primary_exprs[0].id == 'a'
    assert arguments.expressions[0].additive_op == TokenTypes.MINUS
    assert arguments.expressions[0].multipl_exprs[1].primary_exprs[0].id == 'b'
    assert arguments.expressions[1].multipl_exprs[0].primary_exprs[0].id == 'c'
    assert arguments.expressions[1].multipl_exprs[0].multipl_op == TokenTypes.DIVIDE
    assert arguments.expressions[1].multipl_exprs[0].primary_exprs[1].id == 'd'
    assert arguments.expressions[2].multipl_exprs[0].primary_exprs[0].function_call is not None
    assert \
    arguments.expressions[2].multipl_exprs[0].primary_exprs[0].function_call.arguments.expressions[0].multipl_exprs[
        0].primary_exprs[0].id == 'e'
    assert \
    arguments.expressions[2].multipl_exprs[0].primary_exprs[0].function_call.arguments.expressions[1].multipl_exprs[
        0].primary_exprs[0].id == 'f'


def test_empty_arguments():
    parser = create_parser(" ")
    arguments = parser.parse_arguments()
    assert not arguments.expressions


def test_block():  # { statement };
    parser = create_parser("a = b;"
                           "c = d + e;"
                           "print(c);")
    block = parser.parse_block()
    assert block is not None
    assert block.statements[0].id == 'a'
    assert block.statements[0].expression.multipl_exprs[0].primary_exprs[0].id == 'b'
    assert block.statements[1].id == 'c'
    assert block.statements[1].expression.multipl_exprs[0].primary_exprs[0].id == 'd'
    assert block.statements[1].expression.additive_op == TokenTypes.PLUS
    assert block.statements[1].expression.multipl_exprs[1].primary_exprs[0].id == 'e'
    assert isinstance(block.statements[2], PrintStatement)
    assert block.statements[2].printables[0].multipl_exprs[0].primary_exprs[0].id == 'c'


def test_statement():  # ifStatement | whileStatement | returnStatement | initStatement | assignStatement |
    # printStatement | (functionCall, ";") ;
    parser = create_parser("if (a > b) {"
                           "a = b;"
                           "}")
    statement = parser.parse_statement()
    assert isinstance(statement, IfStatement)
    parser = create_parser("while (a >= b) {"
                           "a = a + 1;"
                           "}")
    statement = parser.parse_statement()
    assert isinstance(statement, WhileStatement)
    parser = create_parser("return a+b;")
    statement = parser.parse_statement()
    assert isinstance(statement, ReturnStatement)
    parser = create_parser("dec a = b * c;")
    statement = parser.parse_statement()
    assert isinstance(statement, InitStatement)
    parser = create_parser("dec a;")
    statement = parser.parse_statement()
    assert isinstance(statement, InitStatement)
    parser = create_parser("a = b + c;")
    statement = parser.parse_statement()
    assert isinstance(statement, AssignStatement)
    parser = create_parser(' print ("result: ", a + b, ","); ')
    statement = parser.parse_statement()
    assert isinstance(statement, PrintStatement)
    parser = create_parser('calculate(a, b);')
    statement = parser.parse_statement()
    assert isinstance(statement, FunctionCall)
    parser = create_parser('calculate(a, b)')
    with pytest.raises(_SyntaxError):
        parser.parse_statement()


def test_if_statement():  # “if”, “(”, condition, “)”, “{“, block, “}“ ;
    parser = create_parser("if (a > b) {"
                           "a = b;"
                           "}")
    if_statement = parser.parse_if_statement()
    assert if_statement is not None
    assert \
    if_statement.condition.and_conds[0].equality_conds[0].relational_cond1.primary_cond1.expression.multipl_exprs[
        0].primary_exprs[0].id == 'a'
    assert if_statement.condition.and_conds[0].equality_conds[0].relational_cond1.relation_op == TokenTypes.GREATER_THAN
    assert \
    if_statement.condition.and_conds[0].equality_conds[0].relational_cond1.primary_cond2.expression.multipl_exprs[
        0].primary_exprs[0].id == 'b'
    assert if_statement.block.statements[0].id == 'a'
    assert if_statement.block.statements[0].expression.multipl_exprs[0].primary_exprs[0].id == 'b'


def test_while_statement():  # “if”, “(”, condition, “)”, “{“, block, “}“ ;
    parser = create_parser("while (a >= b) {"
                           "a = a + 1;"
                           "}")
    while_statement = parser.parse_while_statement()
    assert while_statement is not None
    assert \
    while_statement.condition.and_conds[0].equality_conds[0].relational_cond1.primary_cond1.expression.multipl_exprs[
        0].primary_exprs[0].id == 'a'
    assert while_statement.condition.and_conds[0].equality_conds[
               0].relational_cond1.relation_op == TokenTypes.GREATER_OR_EQUAL
    assert \
    while_statement.condition.and_conds[0].equality_conds[0].relational_cond1.primary_cond2.expression.multipl_exprs[
        0].primary_exprs[0].id == 'b'
    assert while_statement.block.statements[0].id == 'a'
    assert while_statement.block.statements[0].expression.multipl_exprs[0].primary_exprs[0].id == 'a'
    assert while_statement.block.statements[0].expression.additive_op == TokenTypes.PLUS
    assert while_statement.block.statements[0].expression.multipl_exprs[1].primary_exprs[0].number == 1


def test_return_statement():
    parser = create_parser("return result;")
    return_statement = parser.parse_return_statement()
    assert return_statement is not None
    assert return_statement.expression.multipl_exprs[0].primary_exprs[0].id == 'result'


def test_return_statement2():
    parser = create_parser("return a+b;")
    return_statement = parser.parse_return_statement()
    assert return_statement is not None
    assert return_statement.expression.multipl_exprs[0].primary_exprs[0].id == 'a'
    assert return_statement.expression.additive_op == TokenTypes.PLUS
    assert return_statement.expression.multipl_exprs[1].primary_exprs[0].id == 'b'


def test_init_statement():  # signature, [ assignmentOp, expression ], “;” ;
    parser = create_parser("dec a;")
    init_statement = parser.parse_init_statement()
    assert init_statement is not None
    assert init_statement.signature.type == TokenTypes.DECIMAL
    assert init_statement.signature.id == 'a'


def test_init_statement2():  # signature, [ assignmentOp, expression ], “;” ;
    parser = create_parser("dec a = b * c;")
    init_statement = parser.parse_init_statement()
    assert init_statement is not None
    assert init_statement.signature.type == TokenTypes.DECIMAL
    assert init_statement.signature.id == 'a'
    assert init_statement.expression.multipl_exprs[0].primary_exprs[0].id == 'b'
    assert init_statement.expression.multipl_exprs[0].multipl_op == TokenTypes.MULTIPLY
    assert init_statement.expression.multipl_exprs[0].primary_exprs[1].id == 'c'


def test_init_statement3():  # signature, [ assignmentOp, expression ], “;” ;
    parser = create_parser("cur a = 5 eur;")
    init_statement = parser.parse_init_statement()
    assert init_statement is not None
    assert init_statement.signature.type == TokenTypes.CURRENCY
    assert init_statement.signature.id == 'a'
    assert init_statement.expression.multipl_exprs[0].primary_exprs[0].number == 5
    assert init_statement.expression.multipl_exprs[0].primary_exprs[0].currency2 == 'eur'
    assert init_statement.expression.multipl_exprs[0].primary_exprs[0].minus is False
    assert init_statement.expression.multipl_exprs[0].primary_exprs[0].currency1 is None
    assert init_statement.expression.multipl_exprs[0].primary_exprs[0].get_currency1 is None
    assert init_statement.expression.multipl_exprs[0].primary_exprs[0].id is None
    assert init_statement.expression.multipl_exprs[0].primary_exprs[0].parenth_expr is None
    assert init_statement.expression.multipl_exprs[0].primary_exprs[0].function_call is None
    assert init_statement.expression.multipl_exprs[0].primary_exprs[0].get_currency2 is None


def test_init_statement4():  # signature, [ assignmentOp, expression ], “;” ;
    parser = create_parser("cur a = b eur;")
    init_statement = parser.parse_init_statement()
    assert init_statement is not None
    assert init_statement.signature.type == TokenTypes.CURRENCY
    assert init_statement.signature.id == 'a'
    assert init_statement.expression.multipl_exprs[0].primary_exprs[0].id == 'b'
    assert init_statement.expression.multipl_exprs[0].primary_exprs[0].currency2 == 'eur'
    assert init_statement.expression.multipl_exprs[0].primary_exprs[0].minus is False
    assert init_statement.expression.multipl_exprs[0].primary_exprs[0].currency1 is None
    assert init_statement.expression.multipl_exprs[0].primary_exprs[0].get_currency1 is None
    assert init_statement.expression.multipl_exprs[0].primary_exprs[0].number is None
    assert init_statement.expression.multipl_exprs[0].primary_exprs[0].parenth_expr is None
    assert init_statement.expression.multipl_exprs[0].primary_exprs[0].function_call is None
    assert init_statement.expression.multipl_exprs[0].primary_exprs[0].get_currency2 is None


def test_print_statement():  # “print”, “(“, printable { “,”, printable }, “)”, ";" ;
    parser = create_parser(' print ("result: ", a + b, ","); ')
    print_statement = parser.parse_print_statement()
    assert print_statement is not None
    assert print_statement.printables[0] == '"result: "'
    assert print_statement.printables[1].multipl_exprs[0].primary_exprs[0].id == 'a'
    assert print_statement.printables[1].additive_op == TokenTypes.PLUS
    assert print_statement.printables[1].multipl_exprs[1].primary_exprs[0].id == 'b'
    assert print_statement.printables[2] == '","'


def test_print_statement2():
    parser = create_parser(' print (a + b, " is result."); ')
    print_statement = parser.parse_print_statement()
    assert print_statement is not None
    assert print_statement.printables[0].multipl_exprs[0].primary_exprs[0].id == 'a'
    assert print_statement.printables[0].additive_op == TokenTypes.PLUS
    assert print_statement.printables[0].multipl_exprs[1].primary_exprs[0].id == 'b'
    assert print_statement.printables[1] == '" is result."'


def test_print_statement3():
    parser = create_parser(' print (a + b, " is", " result.", c); ')
    print_statement = parser.parse_print_statement()
    assert print_statement is not None
    assert print_statement.printables[0].multipl_exprs[0].primary_exprs[0].id == 'a'
    assert print_statement.printables[0].additive_op == TokenTypes.PLUS
    assert print_statement.printables[0].multipl_exprs[1].primary_exprs[0].id == 'b'
    assert print_statement.printables[1] == '" is"'
    assert print_statement.printables[2] == '" result."'
    assert print_statement.printables[3].multipl_exprs[0].primary_exprs[0].id == 'c'


def test_print_statement4():
    parser = create_parser(' print (a + b, " is", c, " result."); ')
    print_statement = parser.parse_print_statement()
    assert print_statement is not None
    assert print_statement.printables[0].multipl_exprs[0].primary_exprs[0].id == 'a'
    assert print_statement.printables[0].additive_op == TokenTypes.PLUS
    assert print_statement.printables[0].multipl_exprs[1].primary_exprs[0].id == 'b'
    assert print_statement.printables[1] == '" is"'
    assert print_statement.printables[2].multipl_exprs[0].primary_exprs[0].id == 'c'
    assert print_statement.printables[3] == '" result."'


def test_empty_print_statement():
    parser = create_parser(' print(); ')
    with pytest.raises(_SyntaxError):
        parser.parse_print_statement()


def test_assign_statement():  # id, assignmentOp, expression, “;” ;
    parser = create_parser("a = b + c;")
    assign_statement = parser.parse_assign_statement_or_function_call()
    assert assign_statement is not None
    assert assign_statement.id == 'a'
    assert assign_statement.expression.multipl_exprs[0].primary_exprs[0].id == 'b'
    assert assign_statement.expression.additive_op == TokenTypes.PLUS
    assert assign_statement.expression.multipl_exprs[1].primary_exprs[0].id == 'c'


def test_assign_statement_with_currency():  # id, assignmentOp, expression, “;” ;
    parser = create_parser("a = 5 eur;")
    assign_statement = parser.parse_assign_statement_or_function_call()
    assert assign_statement is not None
    assert assign_statement.id == 'a'
    assert assign_statement.expression.multipl_exprs[0].primary_exprs[0].number == 5
    assert assign_statement.expression.multipl_exprs[0].primary_exprs[0].currency2 == 'eur'
    assert assign_statement.expression.multipl_exprs[0].primary_exprs[0].minus is False
    assert assign_statement.expression.multipl_exprs[0].primary_exprs[0].currency1 is None
    assert assign_statement.expression.multipl_exprs[0].primary_exprs[0].get_currency1 is None
    assert assign_statement.expression.multipl_exprs[0].primary_exprs[0].id is None
    assert assign_statement.expression.multipl_exprs[0].primary_exprs[0].parenth_expr is None
    assert assign_statement.expression.multipl_exprs[0].primary_exprs[0].function_call is None
    assert assign_statement.expression.multipl_exprs[0].primary_exprs[0].get_currency2 is None


def test_function_call():  # id, “(“, arguments, “)”, “;” ;
    parser = create_parser("calculate(a-b, c/d, e)")
    function_call = parser.parse_assign_statement_or_function_call()
    assert function_call is not None
    assert function_call.id == 'calculate'
    assert function_call.arguments.expressions[0].multipl_exprs[0].primary_exprs[0].id == 'a'
    assert function_call.arguments.expressions[0].additive_op == TokenTypes.MINUS
    assert function_call.arguments.expressions[0].multipl_exprs[1].primary_exprs[0].id == 'b'
    assert function_call.arguments.expressions[1].multipl_exprs[0].primary_exprs[0].id == 'c'
    assert function_call.arguments.expressions[1].multipl_exprs[0].multipl_op == TokenTypes.DIVIDE
    assert function_call.arguments.expressions[1].multipl_exprs[0].primary_exprs[1].id == 'd'
    assert function_call.arguments.expressions[2].multipl_exprs[0].primary_exprs[0].id == 'e'


def test_function_call_with_empty_arguments():  # id, “(“, arguments, “)”, “;” ;
    parser = create_parser("add()")
    function_call = parser.parse_assign_statement_or_function_call()
    assert function_call is not None
    assert function_call.id == 'add'
    assert not function_call.arguments.expressions

    # ------------------------------------CONDITIONS------------------------------------------------------


def test_condition():  # andCond, { orOp, andCond } ;
    parser = create_parser("a==b & c!=d | e<=f")
    condition = parser.parse_condition()
    assert condition is not None
    assert \
    condition.and_conds[0].equality_conds[0].relational_cond1.primary_cond1.expression.multipl_exprs[0].primary_exprs[
        0].id \
    == 'a'
    assert condition.and_conds[0].equality_conds[0].equal_op == TokenTypes.EQUAL
    assert \
    condition.and_conds[0].equality_conds[0].relational_cond2.primary_cond1.expression.multipl_exprs[0].primary_exprs[
        0].id \
    == 'b'
    assert \
    condition.and_conds[0].equality_conds[1].relational_cond1.primary_cond1.expression.multipl_exprs[0].primary_exprs[
        0].id \
    == 'c'
    assert condition.and_conds[0].equality_conds[1].equal_op == TokenTypes.NOT_EQUAL
    assert \
    condition.and_conds[0].equality_conds[1].relational_cond2.primary_cond1.expression.multipl_exprs[0].primary_exprs[
        0].id \
    == 'd'
    assert \
    condition.and_conds[1].equality_conds[0].relational_cond1.primary_cond1.expression.multipl_exprs[0].primary_exprs[
        0].id \
    == 'e'
    assert condition.and_conds[1].equality_conds[0].relational_cond1.relation_op == TokenTypes.LESS_OR_EQUAL
    assert \
    condition.and_conds[1].equality_conds[0].relational_cond1.primary_cond2.expression.multipl_exprs[0].primary_exprs[
        0].id \
    == 'f'


def test_and_cond():  # equalityCond, { andOp, equalityCond } ;
    parser = create_parser("a==b & c!=d")
    and_cond = parser.parse_and_cond()
    assert and_cond is not None
    assert and_cond.equality_conds[0].relational_cond1.primary_cond1.expression.multipl_exprs[0].primary_exprs[0].id \
           == 'a'
    assert and_cond.equality_conds[0].equal_op == TokenTypes.EQUAL
    assert and_cond.equality_conds[0].relational_cond2.primary_cond1.expression.multipl_exprs[0].primary_exprs[0].id \
           == 'b'
    assert and_cond.equality_conds[1].relational_cond1.primary_cond1.expression.multipl_exprs[0].primary_exprs[0].id \
           == 'c'
    assert and_cond.equality_conds[1].equal_op == TokenTypes.NOT_EQUAL
    assert and_cond.equality_conds[1].relational_cond2.primary_cond1.expression.multipl_exprs[0].primary_exprs[0].id \
           == 'd'


def test_equality_cond():  # relationalCond, [ equalOp, relationalCond ] ;
    parser = create_parser("a != b")
    equality_cond = parser.parse_equality_cond()
    assert equality_cond.relational_cond1.primary_cond1.expression.multipl_exprs[0].primary_exprs[0].id == 'a'
    assert equality_cond.equal_op == TokenTypes.NOT_EQUAL
    assert equality_cond.relational_cond2.primary_cond1.expression.multipl_exprs[0].primary_exprs[0].id == 'b'


def test_relational_cond():  # primaryCond, [ relationOp, primaryCond ];
    parser = create_parser("a > b")
    relational_cond = parser.parse_relational_cond()
    assert relational_cond.primary_cond1.expression.multipl_exprs[0].primary_exprs[0].id == 'a'
    assert relational_cond.relation_op == TokenTypes.GREATER_THAN
    assert relational_cond.primary_cond2.expression.multipl_exprs[0].primary_exprs[0].id == 'b'


def test_relational_cond_with_number():  # primaryCond, [ relationOp, primaryCond ];
    parser = create_parser("a > 0")
    relational_cond = parser.parse_relational_cond()
    assert relational_cond.primary_cond1.expression.multipl_exprs[0].primary_exprs[0].id == 'a'
    assert relational_cond.relation_op == TokenTypes.GREATER_THAN
    assert relational_cond.primary_cond2.expression.multipl_exprs[0].primary_exprs[0].number == 0


# def test_primary_cond():  # [ unaryOp ], ( parenthCond | expression ) ;
#     parser = create_parser("!a")
#     primary_cond = parser.parse_primary_cond()
#     assert primary_cond.unary_op is True
#     assert primary_cond.expression.multipl_exprs[0].primary_exprs[0].id == 'a'
#
#
# def test_primary_cond2():  # [ unaryOp ], ( parenthCond | expression ) ;
#     parser = create_parser("!(a > b)")
#     primary_cond = parser.parse_primary_cond()
#     assert primary_cond is not None
#     assert primary_cond.parenth_cond is not None
#     assert primary_cond.expression is None


def test_parenth_cond():
    parser = create_parser("(a==b & c!=d | e<=f)")
    parenth_cond = parser.parse_parenth_cond()
    assert parenth_cond is not None
    assert parenth_cond.condition.and_conds[0].equality_conds[
               0].relational_cond1.primary_cond1.expression.multipl_exprs[0].primary_exprs[0].id == 'a'
    assert parenth_cond.condition.and_conds[0].equality_conds[
               0].equal_op == TokenTypes.EQUAL
    assert parenth_cond.condition.and_conds[0].equality_conds[
               0].relational_cond2.primary_cond1.expression.multipl_exprs[0].primary_exprs[0].id == 'b'
    assert parenth_cond.condition.and_conds[0].equality_conds[
               1].relational_cond1.primary_cond1.expression.multipl_exprs[0].primary_exprs[0].id == 'c'
    assert parenth_cond.condition.and_conds[0].equality_conds[
               1].equal_op == TokenTypes.NOT_EQUAL
    assert parenth_cond.condition.and_conds[0].equality_conds[
               1].relational_cond2.primary_cond1.expression.multipl_exprs[0].primary_exprs[0].id == 'd'
    assert parenth_cond.condition.and_conds[1].equality_conds[
               0].relational_cond1.primary_cond1.expression.multipl_exprs[0].primary_exprs[0].id == 'e'
    assert parenth_cond.condition.and_conds[1].equality_conds[
               0].relational_cond1.relation_op == TokenTypes.LESS_OR_EQUAL
    assert parenth_cond.condition.and_conds[1].equality_conds[
               0].relational_cond1.primary_cond2.expression.multipl_exprs[0].primary_exprs[0].id == 'f'

    # ------------------------------------EXPRESSIONS------------------------------------------------------


def test_expression():  # multiplExpr, { additiveOp, multiplExpr } ;
    parser = create_parser("a * b + c")
    expression = parser.parse_expression()
    assert expression.multipl_exprs[0].primary_exprs[0].id == 'a'
    assert expression.multipl_exprs[0].multipl_op == TokenTypes.MULTIPLY
    assert expression.multipl_exprs[0].primary_exprs[1].id == 'b'
    assert expression.additive_op == TokenTypes.PLUS
    assert expression.multipl_exprs[1].primary_exprs[0].id == 'c'


def test_expression_with_number_only():  # multiplExpr, { additiveOp, multiplExpr } ;
    parser = create_parser("5")
    expression = parser.parse_expression()
    assert expression is not None
    assert expression.multipl_exprs[0].primary_exprs[0].number == 5


def test_expression_with_zero_only():  # multiplExpr, { additiveOp, multiplExpr } ;
    parser = create_parser("0")
    expression = parser.parse_expression()
    assert expression is not None
    assert expression.multipl_exprs[0].primary_exprs[0].number == 0


def test_multipl_expr():  # primaryExpr, { multiplOp, primaryExpr } ;
    parser = create_parser("a * 5")
    multipl_expr = parser.parse_multipl_expr()
    assert multipl_expr.primary_exprs[0].id == 'a'
    assert multipl_expr.multipl_op == TokenTypes.MULTIPLY
    assert multipl_expr.primary_exprs[1].number == 5


def test_primary_expr():  # def __init__(self, minus=False, currency1=None, get_currency1=None, number=None,
    # _id=None, parenth_expr=None, function_call=None, currency2=None, get_currency2=None):
    parser = create_parser("a.get_currency() b")
    primary_expr = parser.parse_primary_expr()
    assert primary_expr is not None
    assert primary_expr.minus is False
    assert primary_expr.currency1 is None
    assert primary_expr.get_currency1.id == 'a'
    assert primary_expr.number is None
    assert primary_expr.id == 'b'
    assert primary_expr.parenth_expr is None
    assert primary_expr.function_call is None
    assert primary_expr.currency2 is None
    assert primary_expr.get_currency2 is None


def test_primary_expr2():  # def __init__(self, minus=False, currency1=None, get_currency1=None, number=None,
    # _id=None, parenth_expr=None, function_call=None, currency2=None, get_currency2=None):
    parser = create_parser("-b")
    primary_expr = parser.parse_primary_expr()
    assert primary_expr is not None
    assert primary_expr.minus is True
    assert primary_expr.currency1 is None
    assert primary_expr.get_currency1 is None
    assert primary_expr.number is None
    assert primary_expr.id == 'b'
    assert primary_expr.parenth_expr is None
    assert primary_expr.function_call is None
    assert primary_expr.currency2 is None
    assert primary_expr.get_currency2 is None


def test_primary_expr3():  # def __init__(self, minus=False, currency1=None, get_currency1=None, number=None,
    # _id=None, parenth_expr=None, function_call=None, currency2=None, get_currency2=None):
    parser = create_parser("b usd")
    primary_expr = parser.parse_primary_expr()
    assert primary_expr is not None
    assert primary_expr.minus is False
    assert primary_expr.currency1 is None
    assert primary_expr.get_currency1 is None
    assert primary_expr.number is None
    assert primary_expr.id == 'b'
    assert primary_expr.parenth_expr is None
    assert primary_expr.function_call is None
    assert primary_expr.currency2 == 'usd'
    assert primary_expr.get_currency2 is None


def test_primary_expr4():  # def __init__(self, minus=False, currency1=None, get_currency1=None, number=None,
    # _id=None, parenth_expr=None, function_call=None, currency2=None, get_currency2=None):
    parser = create_parser("a.get_currency() b usd")
    primary_expr = parser.parse_primary_expr()
    assert primary_expr is not None
    assert primary_expr.minus is False
    assert primary_expr.currency1 is None
    assert primary_expr.get_currency1.id == 'a'
    assert primary_expr.number is None
    assert primary_expr.id == 'b'
    assert primary_expr.parenth_expr is None
    assert primary_expr.function_call is None
    assert primary_expr.currency2 == 'usd'
    assert primary_expr.get_currency2 is None


def test_primary_expr5():  # def __init__(self, minus=False, currency1=None, get_currency1=None, number=None,
    # _id=None, parenth_expr=None, function_call=None, currency2=None, get_currency2=None):
    parser = create_parser("usd b a.get_currency()")
    primary_expr = parser.parse_primary_expr()
    assert primary_expr is not None
    assert primary_expr.minus is False
    assert primary_expr.currency1 == 'usd'
    assert primary_expr.get_currency1 is None
    assert primary_expr.number is None
    assert primary_expr.id == 'b'
    assert primary_expr.parenth_expr is None
    assert primary_expr.function_call is None
    assert primary_expr.currency2 is None
    assert primary_expr.get_currency2.id == 'a'


def test_primary_expr6():  # def __init__(self, minus=False, currency1=None, get_currency1=None, number=None,
    # _id=None, parenth_expr=None, function_call=None, currency2=None, get_currency2=None):
    parser = create_parser("usd 5.2 a.get_currency()")
    primary_expr = parser.parse_primary_expr()
    assert primary_expr is not None
    assert primary_expr.minus is False
    assert primary_expr.currency1 == 'usd'
    assert primary_expr.get_currency1 is None
    assert primary_expr.number == 5.2
    assert primary_expr.id is None
    assert primary_expr.parenth_expr is None
    assert primary_expr.function_call is None
    assert primary_expr.currency2 is None
    assert primary_expr.get_currency2.id == 'a'


def test_primary_expr7():  # def __init__(self, minus=False, currency1=None, get_currency1=None, number=None,
    # _id=None, parenth_expr=None, function_call=None, currency2=None, get_currency2=None):
    parser = create_parser("a.get_currency() 5.2 usd")
    primary_expr = parser.parse_primary_expr()
    assert primary_expr is not None
    assert primary_expr.minus is False
    assert primary_expr.currency1 is None
    assert primary_expr.get_currency1.id == 'a'
    assert primary_expr.number == 5.2
    assert primary_expr.id is None
    assert primary_expr.parenth_expr is None
    assert primary_expr.function_call is None
    assert primary_expr.currency2 == 'usd'
    assert primary_expr.get_currency2 is None


def test_primary_expr8():  # def __init__(self, minus=False, currency1=None, get_currency1=None, number=None,
    # _id=None, parenth_expr=None, function_call=None, currency2=None, get_currency2=None):
    parser = create_parser("usd calculate(a, b)")
    primary_expr = parser.parse_primary_expr()
    assert primary_expr is not None
    assert primary_expr.minus is False
    assert primary_expr.currency1 == 'usd'
    assert primary_expr.get_currency1 is None
    assert primary_expr.number is None
    assert primary_expr.id is None
    assert primary_expr.parenth_expr is None
    assert primary_expr.function_call.id == 'calculate'
    assert primary_expr.currency2 is None
    assert primary_expr.get_currency2 is None


def test_primary_expr9():  # def __init__(self, minus=False, currency1=None, get_currency1=None, number=None,
    # _id=None, parenth_expr=None, function_call=None, currency2=None, get_currency2=None):
    parser = create_parser("a.get_currency() calculate(a, b) b.get_currency()")
    primary_expr = parser.parse_primary_expr()
    assert primary_expr is not None
    assert primary_expr.minus is False
    assert primary_expr.currency1 is None
    assert primary_expr.get_currency1.id == 'a'
    assert primary_expr.number is None
    assert primary_expr.id is None
    assert primary_expr.parenth_expr is None
    assert primary_expr.function_call.id == 'calculate'
    assert primary_expr.currency2 is None
    assert primary_expr.get_currency2.id == 'b'


def test_primary_expr10():  # def __init__(self, minus=False, currency1=None, get_currency1=None, number=None,
    # _id=None, parenth_expr=None, function_call=None, currency2=None, get_currency2=None):
    parser = create_parser("calculate(a, b)")
    primary_expr = parser.parse_primary_expr()
    assert primary_expr is not None
    assert primary_expr.minus is False
    assert primary_expr.currency1 is None
    assert primary_expr.get_currency1 is None
    assert primary_expr.number is None
    assert primary_expr.id is None
    assert primary_expr.parenth_expr is None
    assert primary_expr.function_call is not None
    assert primary_expr.function_call.id == 'calculate'
    assert primary_expr.function_call.arguments.expressions[0].multipl_exprs[0].primary_exprs[0].id == 'a'
    assert primary_expr.function_call.arguments.expressions[1].multipl_exprs[0].primary_exprs[0].id == 'b'
    assert primary_expr.currency2 is None
    assert primary_expr.get_currency2 is None


def test_primary_expr11():  # def __init__(self, minus=False, currency1=None, get_currency1=None, number=None,
    # _id=None, parenth_expr=None, function_call=None, currency2=None, get_currency2=None):
    parser = create_parser("- a.get_currency() (c * d + e) b.get_currency()")
    primary_expr = parser.parse_primary_expr()
    assert primary_expr is not None
    assert primary_expr.minus is True
    assert primary_expr.currency1 is None
    assert primary_expr.get_currency1.id == 'a'
    assert primary_expr.number is None
    assert primary_expr.id is None
    assert primary_expr.parenth_expr is not None
    assert primary_expr.parenth_expr.expression.multipl_exprs[0].primary_exprs[0].id == 'c'
    assert primary_expr.parenth_expr.expression.multipl_exprs[0].multipl_op == TokenTypes.MULTIPLY
    assert primary_expr.parenth_expr.expression.multipl_exprs[0].primary_exprs[1].id == 'd'
    assert primary_expr.parenth_expr.expression.additive_op == TokenTypes.PLUS
    assert primary_expr.parenth_expr.expression.multipl_exprs[1].primary_exprs[0].id == 'e'
    assert primary_expr.function_call is None
    assert primary_expr.currency2 is None
    assert primary_expr.get_currency2.id == 'b'


def test_primary_expr12():  # def __init__(self, minus=False, currency1=None, get_currency1=None, number=None,
    # _id=None, parenth_expr=None, function_call=None, currency2=None, get_currency2=None):
    parser = create_parser("(c * d + e) usd")
    primary_expr = parser.parse_primary_expr()
    assert primary_expr is not None
    assert primary_expr.minus is False
    assert primary_expr.currency1 is None
    assert primary_expr.get_currency1 is None
    assert primary_expr.number is None
    assert primary_expr.id is None
    assert primary_expr.parenth_expr is not None
    assert primary_expr.parenth_expr.expression.multipl_exprs[0].primary_exprs[0].id == 'c'
    assert primary_expr.parenth_expr.expression.multipl_exprs[0].multipl_op == TokenTypes.MULTIPLY
    assert primary_expr.parenth_expr.expression.multipl_exprs[0].primary_exprs[1].id == 'd'
    assert primary_expr.parenth_expr.expression.additive_op == TokenTypes.PLUS
    assert primary_expr.parenth_expr.expression.multipl_exprs[1].primary_exprs[0].id == 'e'
    assert primary_expr.function_call is None
    assert primary_expr.currency2 == 'usd'
    assert primary_expr.get_currency2 is None


def test_primary_expr13():  # def __init__(self, minus=False, currency1=None, get_currency1=None, number=None,
    # _id=None, parenth_expr=None, function_call=None, currency2=None, get_currency2=None):
    parser = create_parser("5")
    primary_expr = parser.parse_primary_expr()
    assert primary_expr is not None
    assert primary_expr.minus is False
    assert primary_expr.currency1 is None
    assert primary_expr.get_currency1 is None
    assert primary_expr.number == 5
    assert primary_expr.id is None
    assert primary_expr.parenth_expr is None
    assert primary_expr.function_call is None
    assert primary_expr.currency2 is None
    assert primary_expr.get_currency2 is None


def test_parenth_expr():
    parser = create_parser("(a * b + c)")
    parenth_expr = parser.parse_parenth_expr()
    assert parenth_expr.expression.multipl_exprs[0].primary_exprs[0].id == 'a'
    assert parenth_expr.expression.multipl_exprs[0].multipl_op == TokenTypes.MULTIPLY
    assert parenth_expr.expression.multipl_exprs[0].primary_exprs[1].id == 'b'
    assert parenth_expr.expression.additive_op == TokenTypes.PLUS
    assert parenth_expr.expression.multipl_exprs[1].primary_exprs[0].id == 'c'

    # ------------------------------------------------------------------------------------------------------------


def test_get_currency():
    parser = create_parser("var.get_currency()")
    assert parser.parse_get_currency().id == 'var'


def test_incorrect_get_currency():
    parser = create_parser("var.get_currency(")
    assert parser.parse_get_currency() is None


def test_incorrect_get_currency2():
    parser = create_parser("var,get_currency(")
    assert parser.parse_get_currency() is None
