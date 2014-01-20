from pyparsing import *

from elements import *
from traversal import *

def ast(self, nodetype):
    self.setParseAction(lambda toks: AST(nodetype, toks))
    return self

ParserElement.ast = ast

integer = Combine(Optional('-') + Word(nums)).setParseAction(lambda toks: AST('integer', [int(toks[0])] ))

real =  Combine(Optional('-') + Word(nums) + '.' + Word(nums)).setParseAction(lambda toks: AST('real', [float(toks[0])] ))

variableName = Word(alphas + '_%$@', alphanums + '_').ast('variableName')

placeholder = (Suppress('|') + variableName + Suppress('|')).ast('placeholder')

identifier = ( (variableName | placeholder) + ZeroOrMore(variableName | placeholder) ).ast('identifier')

expression = Forward()
index = (Suppress('[') + delimitedList(expression) + Suppress(']')).ast('index')

timeOffset = (Suppress('(') + (integer | variableName) + Suppress(')')).ast('timeOffset')

array = (identifier + index + Optional(timeOffset, default = None)).ast('array')

operand = array | identifier | real | integer

unaryOperator = oneOf('+ -').ast('operator')

operator = oneOf('+ - * / ^').ast('operator')

comparisonOperator = oneOf('<> < <= > >= ==').ast("comparisonOperator")

booleanOperator = oneOf('and or xor').ast("booleanOperator")

formula = Forward()

func = (variableName + Suppress('(') + (formula ^ delimitedList(expression)) + Suppress(')')).ast("function")

openParen = Literal('(').ast('literal')
closeParen = Literal(')').ast('literal')

atom = func | openParen + expression + closeParen | operand
expression << Optional(unaryOperator) + atom + ZeroOrMore((operator | comparisonOperator | booleanOperator) + atom)
expression = expression.ast('expression')

equation = (expression + Suppress('=') + expression).ast('equation')

condition = (Suppress(Keyword('if')) + expression).ast('condition')

lstBase  = OneOrMore(Word(alphanums).ast('string')).ast('listBase')
lst = (lstBase + Optional(Suppress('\\') + lstBase, default = ASTNone)).ast('list')

def grouped(elem):
    return elem | (Suppress('(') + delimitedList(elem) + Suppress(')'))

iter = (grouped(variableName) + Suppress(Keyword('in')) + grouped(lst | variableName)).ast('iterator')

options = oneOf('!pv !p !Pv !P').setParseAction(lambda toks: toks[0])

formula << (Optional(options, default = None) +
            (equation | expression) +
            Optional(condition, default = None) +
            Optional(Suppress(',') + delimitedList(iter), default = None)).ast('formula')

