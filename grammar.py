from pyparsing import *

from elements import *

def tokensAsList(kls, tokens):
    return kls(tokens.asList())

def tokensAsArguments(kls, tokens):
    return kls(*tokens.asList())

def setParseClass(self, kls, unpack = False):
    self.setParseAction(partial(tokensAsArguments if unpack else tokensAsList, kls))
    return self

ParserElement.setParseClass = setParseClass

integer = Combine(Optional('-') + Word(nums)).setParseAction(lambda toks: Integer(int(toks[0])))

real =  Combine(Optional('-') + Word(nums) + '.' + Word(nums)).setParseAction(lambda toks: Real(float(toks[0])))

variableName = Word(alphas + '_', alphanums + '_').setParseClass(VariableName, True)

placeholder = (Suppress('|') + variableName + Suppress('|')).setParseClass(Placeholder, True)

identifier = ( (variableName | placeholder) + ZeroOrMore(variableName | placeholder) ).setParseClass(Identifier)

index = (Suppress('[') + delimitedList(variableName | integer) + Suppress(']')).setParseClass(Index)

array = (identifier + index).setParseClass(Array, True)

expression = Forward()
operand = array | identifier | real | integer

operator = oneOf('+ - * / ^').setParseClass(Operator, True)

comparisonOperator = oneOf('<> < <= > >= ==').setParseClass(ComparisonOperator, True)

booleanOperator = oneOf('and or xor').setParseClass(BooleanOperator, True)

func = (oneOf('exp log d') + Suppress('(') + expression + Suppress(')')).setParseClass(Func, True)

atom =  func | '(' + expression + ')' | operand
expression << atom + ZeroOrMore((operator | comparisonOperator | booleanOperator) + atom)
expression = expression.setParseClass(Expression)

equation = (expression + Suppress('=') + expression).setParseClass(Equation, True)

condition = (Suppress(Keyword('if')) + expression).setParseClass(Condition, True)

lst = OneOrMore(Word(alphanums)).setParseClass(Lst)

iter = (variableName + Suppress(Keyword('in')) + (lst | variableName)).setParseClass(Iter, True)

options = oneOf('!pv !p !Pv !P').setParseAction(lambda toks: toks[0])

formula = (Group(Optional(options)) +
           equation +
           Group(Optional(condition)) +
           Group(Optional(Suppress(',') + delimitedList(iter)))).setParseClass(Formula, True)
