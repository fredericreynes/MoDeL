from collections import *
from pyparsing import *
from funcy import *

import itertools

def tokensAsList(kls, tokens):
    return kls(tokens.asList())

def tokensAsArguments(kls, tokens):
    return kls(*tokens.asList())

def setParseClass(self, kls, unpack = False):
    self.setParseAction(partial(tokensAsArguments if unpack else tokensAsList, kls))
    return self

ParserElement.setParseClass = setParseClass

class BaseElement(namedtuple("BaseElement", ['value'])):
    def compile(self, bindings):
        return str(self.value)

# Numerical types
class Integer(BaseElement): pass
integer = Combine(Optional('-') + Word(nums)).setParseAction(lambda toks: Integer(int(toks[0])))

class Real(BaseElement): pass
real =  Combine(Optional('-') + Word(nums) + '.' + Word(nums)).setParseAction(lambda toks: Real(float(toks[0])))

# A VariableName must start with an alphabetical character or an underscore,
# and can contain any number of alphanumerical characters or underscores
class VariableName(BaseElement): pass
variableName = Word(alphas + '_', alphanums + '_').setParseClass(VariableName, True)

# A Placeholder is a VariableName enclosed in curly brackets, e.g. `{X}`
class Placeholder(BaseElement): pass
placeholder = (Suppress('{') + variableName + Suppress('}')).setParseClass(Placeholder, True)

# An identifier is a combination of one or more VariableNames and Placeholders
# e.g. {V}_energy, or Price{O}
class Identifier(BaseElement): pass
identifier = ( (variableName | placeholder) + ZeroOrMore(variableName | placeholder) ).setParseClass(Identifier)

# An Index is used in an Array to address its individual elements
# It can have multiple dimensions, e.g. [com, sec]
class Index(BaseElement): pass
index = (Suppress('[') + delimitedList(variableName | integer) + Suppress(']')).setParseClass(Index)

# An Array is a combination of a Identifier and an Index
Array = namedtuple("Array", ['identifier', 'index'])
array = (identifier + index).setParseClass(Array, True)

# An Expression is the building block of an equation
# Expressions can include operators, functions and any operand (Array, Identifier, or number)
Expression = namedtuple("Expression", ['value'])
expression = Forward()
operand = array | identifier | real | integer

Operator = namedtuple("Operator", ['value'])
operator = oneOf('+ - * / ^').setParseClass(Operator)

Func = namedtuple("Func", ['name', 'expression'])
func = (oneOf('exp log d') + Suppress('(') + expression + Suppress(')')).setParseClass(Func, True)

atom =  func | '(' + expression + ')' | operand
expression << atom + ZeroOrMore(operator + atom)
expression = expression.setParseClass(Expression)

# An Equation is made of two Expressions separated by an equal sign
Equation = namedtuple("Equation", ['lhs', 'rhs'])
equation = (expression + Suppress('=') + expression).setParseClass(Equation, True)

# A Lst is a sequence of space-delimited strings (usually numbers), used for an iterator
# e.g. 01 02 03 04 05 06
Lst = namedtuple("Lst", ['value'])
lst = OneOrMore(Word(alphanums)).setParseClass(Lst)

# An Iterator is the combination of a VariableName and a Lst
# Each occurence of the VariableName inside an Index or a Placeholder will be replaced
# with each value in the Lst, sequentially, at the compile stage
# e.g. com in 01 02 03 04 05 06 07 08 09
Iter = namedtuple("Iter", ['variableName', 'lst'])
iter = (variableName + Suppress(Keyword('in')) + (lst | variableName)).setParseClass(Iter, True)

# A Formula is the combination of an equation and of one or more Iter(ators)
# This is the full form of the code passed from eViews to the compiler
# e.g. {V}[com] = {V}D[com] + {V}M[com], V in Q CH G I DS, com in 01 02 03 04 05 06 07 08 09
Formula = namedtuple("Formula", ['equation', 'iterators'])
formula = (equation + Group(Optional(Suppress(',') + delimitedList(iter)))).setParseClass(Formula, True)
