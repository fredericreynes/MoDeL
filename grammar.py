from pyparsing import *

from elements import *

def tokensAsList(kls, tokens):
    return kls(tokens.asList())

def tokensAsArguments(kls, tokens):
    return kls(*tokens.asList())

def setParseClass(self, kls, unpack = False):
    self.setParseAction(partial(tokensAsArguments if unpack else tokensAsList, kls))
    return self

def ast(self, nodetype, hasValue = False):
    def astLambda(toks):
        if hasValue:
            if len(toks) > 1:
                return AST(nodetype, value = toks[0], children = toks[1:])
            else:
                return AST(nodetype, value = toks[0])
        else:
            return AST(nodetype, children = toks)

    self.setParseAction(astLambda)
    return self


ParserElement.setParseClass = setParseClass
ParserElement.ast = ast

class AST:
    def __init__(self, nodetype, value = None, children = None):
        self.nodetype = nodetype
        self.value = value
        self.children = children

    def has_value(self):
        return not self.value is None

    def has_children(self):
        return not self.children is None

    def __str__(self):
        base = self.nodetype + ": "
        if self.has_value() and self.has_children():
            return base + str(self.value) + ", (" + ', '.join([str(e) for e in self.children])  + ")"
        elif self.has_value():
            return base + str(self.value)
        elif self.has_children():
            return base + '(' + ', '.join([str(e) for e in self.children]) + ')'
        else:
            return base

integer = Combine(Optional('-') + Word(nums)).setParseAction(lambda toks: AST('integer', value = int(toks[0])))

real =  Combine(Optional('-') + Word(nums) + '.' + Word(nums)).setParseAction(lambda toks: AST('real', value = float(toks[0])))

variableName = Word(alphas + '_%$@', alphanums + '_').ast('variableName', True)

placeholder = (Suppress('|') + variableName + Suppress('|')).ast('placeholder')

identifier = ( (variableName | placeholder) + ZeroOrMore(variableName | placeholder) ).ast('identifier')

expression = Forward()
index = (Suppress('[') + delimitedList(expression) + Suppress(']')).setParseClass(Index)

timeOffset = (Suppress('(') + (integer | variableName) + Suppress(')')).setParseClass(TimeOffset, True)

array = (identifier + index + Group(Optional(timeOffset))).setParseClass(Array, True)

operand = array | identifier | real | integer

unaryOperator = oneOf('+ -').setParseClass(Operator, True)

operator = oneOf('+ - * / ^').setParseClass(Operator, True)

comparisonOperator = oneOf('<> < <= > >= ==').setParseClass(ComparisonOperator, True)

booleanOperator = oneOf('and or xor').setParseClass(BooleanOperator, True)

func = (variableName + Suppress('(') + Group(delimitedList(expression)) + Suppress(')')).setParseClass(Func, True)

formula = Forward()
sumFunc = (Suppress('sum') + Suppress('(') + formula + Suppress(')')).setParseClass(SumFunc, True)

openParen = Literal('(').setParseClass(BaseElement, True)
closeParen = Literal(')').setParseClass(BaseElement, True)

atom =  sumFunc | func | openParen + expression + closeParen | operand
expression << Optional(unaryOperator) + atom + ZeroOrMore((operator | comparisonOperator | booleanOperator) + atom)
expression = expression.setParseClass(Expression)

equation = (expression + Suppress('=') + expression).setParseClass(Equation, True)

condition = (Suppress(Keyword('if')) + expression).setParseClass(Condition, True)

lstRaw  = OneOrMore(Word(alphanums))
lst = (Group(lstRaw) + Group(Optional(Suppress('\\') + lstRaw))).setParseClass(Lst, True)

iter = (variableName + Suppress(Keyword('in')) + (lst | variableName)).setParseClass(Iter, True)

options = oneOf('!pv !p !Pv !P').setParseAction(lambda toks: toks[0])

formula << (Group(Optional(options)) +
            (equation | expression) +
            Group(Optional(condition)) +
            Group(Optional(Suppress(',') + delimitedList(iter)))).setParseClass(Formula, True)

print identifier.parseString('test|X|_energy|O|')[0]
