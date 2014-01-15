from pyparsing import *

from elements import *

def tokensAsList(kls, tokens):
    return kls(tokens.asList())

def tokensAsArguments(kls, tokens):
    return kls(*tokens.asList())

def setParseClass(self, kls, unpack = False):
    self.setParseAction(partial(tokensAsArguments if unpack else tokensAsList, kls))
    return self

def ast(self, nodetype):
    self.setParseAction(lambda toks: AST(nodetype, toks))
    return self


ParserElement.setParseClass = setParseClass
ParserElement.ast = ast

class AST:
    def __init__(self, nodetype, children):
        self.nodetype = nodetype
        self.children = children

    @property
    def is_immediate(self):
        return len(self.children) == 1 and not isinstance(self.children[0], AST)

    @property
    def immediate(self):
        if self.is_immediate:
            return self.children[0]
        else:
            raise TypeError

    def __str__(self):
        base = self.nodetype + ": "
        if self.is_immediate:
            return base + repr(self.children[0])
        else:
            return base + '(' + ', '.join([str(e) for e in self.children]) + ')'

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

func = (variableName + Suppress('(') + delimitedList(expression) + Suppress(')')).ast("function")
formulaFunc = (variableName + Suppress('(') + formula + Suppress(')')).ast("formulaFunction")

openParen = Literal('(').ast('literal')
closeParen = Literal(')').ast('literal')

atom =  func | openParen + expression + closeParen | operand
expression << Optional(unaryOperator) + atom + ZeroOrMore((operator | comparisonOperator | booleanOperator) + atom)
expression = expression.ast('expression')

equation = (expression + Suppress('=') + expression).ast('equation')

condition = (Suppress(Keyword('if')) + expression).ast('condition')

lstBase  = OneOrMore(Word(alphanums).ast('string')).ast('listBase')
lst = (lstBase + Optional(Suppress('\\') + lstBase, default = None)).ast('list')

iter = (variableName + Suppress(Keyword('in')) + (lst | variableName)).ast('iterator')

options = oneOf('!pv !p !Pv !P').setParseAction(lambda toks: toks[0])

formula << (Group(Optional(options)) +
            (equation | expression) +
            Group(Optional(condition)) +
            Group(Optional(Suppress(',') + delimitedList(iter)))).setParseClass(Formula, True)

print identifier.parseString('test|X|_energy|O|')[0]
