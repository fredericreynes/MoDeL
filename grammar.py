from pyparsing import *

from elements import *
from traversal import *
from adjacent import Adjacent

def ast(self, nodetype):
    self.setParseAction(lambda toks: AST(nodetype, toks))
    return self

ParserElement.ast = ast

integer = Combine(Optional('-') + Word(nums)).setParseAction(lambda toks: AST('integer', [int(toks[0])] ))

real =  Combine(Optional('-') + Word(nums) + '.' + Word(nums)).setParseAction(lambda toks: AST('real', [float(toks[0])] ))

varNameChars = alphanums + '_'

variableName = Word(alphas + '_@', varNameChars).ast('variableName')

localName = Word('%', varNameChars).ast('localName')

loopCounter = Word('$', varNameChars).ast('loopCounter')

placeholder = Adjacent(Suppress('|') + (variableName | localName) + Suppress('|')).ast('placeholder')

identifier = Adjacent( (variableName | localName | placeholder) + ZeroOrMore(variableName | localName | placeholder) ).ast('identifier')

expression = Forward()
index = (Suppress('[') + delimitedList(expression) + Suppress(']')).ast('index')

timeOffset = (Suppress('(') + (integer | variableName) + Suppress(')')).ast('timeOffset')

array = Adjacent(identifier + index + Optional(timeOffset, default = ASTNone)).ast('array')

operand = array | identifier | loopCounter | real | integer

unaryOperator = oneOf('+ -').ast('operator')

operator = oneOf('+ - * / ^').ast('operator')

comparisonOperator = oneOf('<> < <= =< > >= => ==').ast("comparisonOperator")

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
lst = ((lstBase | localName) + Optional(Suppress('\\') + (lstBase | localName), default = ASTNone)).ast('list')

def grouped(elem):
    return (elem | (Suppress('(') + delimitedList(elem) + Suppress(')'))).ast('group')

iter = (grouped(variableName) + Suppress(Keyword('in')) + grouped(lst)).ast('iterator')

options = oneOf('!pv !p !Pv !P @pv @PV @Pv @pV').ast('string')

formula << (Optional(options, default = ASTNone) +
            (equation | expression) +
            Optional(condition, default = ASTNone) +
            Optional(Suppress('where') + delimitedList(iter ^ variableName), default = ASTNone)).ast('formula')

assignment = (grouped(localName) + Suppress(':=') + grouped(lst | localName)).ast('assignment')

instruction = (iter | assignment | formula).ast('instruction')

# ce2_iter = compile_ast(iter.parseString("ce2 in 21 22 24")[0]).compiled
# s_iter = compile_ast(iter.parseString("s in 01 02 03")[0]).compiled
# ast = formula.parseString("TCO_VAL_sec[ce2] = sum(TCO_VAL[ce2, s], s in 01 02 03)")[0]
# print generate(compile_ast(ast, heap = {'s': s_iter, 'ce2': ce2_iter}))
