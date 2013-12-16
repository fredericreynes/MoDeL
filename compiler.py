from collections import *
from pyparsing import *
from funcy import *

import itertools
import csv

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

# Used to mark parsed elements that contain immediate (ie constant) values
class Immediate: pass

# Numerical types
class Integer(BaseElement, Immediate): pass
integer = Combine(Optional('-') + Word(nums)).setParseAction(lambda toks: Integer(int(toks[0])))

class Real(BaseElement, Immediate): pass
real =  Combine(Optional('-') + Word(nums) + '.' + Word(nums)).setParseAction(lambda toks: Real(float(toks[0])))

# A VariableName must start with an alphabetical character or an underscore,
# and can contain any number of alphanumerical characters or underscores
class VariableName(BaseElement): pass
variableName = Word(alphas + '_', alphanums + '_').setParseClass(VariableName, True)

# A Placeholder is a VariableName enclosed in curly brackets, e.g. `{X}`
class Placeholder(BaseElement):
    def compile(self, bindings):
        return bindings[self.value]

placeholder = (Suppress('{') + variableName + Suppress('}')).setParseClass(Placeholder, True)

class HasIteratedVariables:
    def getIteratedVariableNames(self): raise NotImplementedError

# An identifier is a combination of one or more VariableNames and Placeholders
# e.g. {V}_energy, or Price{O}
class Identifier(BaseElement, HasIteratedVariables):
    def getIteratedVariableNames(self):
        return [e.value for e in self.value if isinstance(e, Placeholder)]

    def compile(self, bindings):
        return ''.join([e.compile(bindings) for e in self.value])

identifier = ( (variableName | placeholder) + ZeroOrMore(variableName | placeholder) ).setParseClass(Identifier)

# An Index is used in an Array to address its individual elements
# It can have multiple dimensions, e.g. [com, sec]
class Index(BaseElement, HasIteratedVariables):
    def getIteratedVariableNames(self):
        return self.value

    def compile(self, bindings):
        return '_'.join([bindings[v] if isinstance(v, VariableName) else
                         v.compile(bindings) for v in self.value])

index = (Suppress('[') + delimitedList(variableName | integer) + Suppress(']')).setParseClass(Index)

# An Array is a combination of a Identifier and an Index
class Array(namedtuple("Array", ['identifier', 'index']), HasIteratedVariables):
    def getIteratedVariableNames(self):
        return self.identifier.getIteratedVariableNames() + self.index.getIteratedVariableNames()

    def compile(self, bindings):
        return self.identifier.compile(bindings) + '_' + self.index.compile(bindings)

array = (identifier + index).setParseClass(Array, True)

# An Expression is the building block of an equation
# Expressions can include operators, functions and any operand (Array, Identifier, or number)
class Expression(namedtuple("Expression", ['value']), HasIteratedVariables):
    def getIteratedVariableNames(self):
        return list(itertools.chain(*[e.getIteratedVariableNames() for e in self.value if isinstance(e, HasIteratedVariables)]))

    def compile(self, bindings):
        return ' '.join([e.compile(bindings) for e in self.value])

    def evaluate(self, bindings, heap):
        return eval(' '.join([e.compile(bindings) if isinstance(e, Immediate) else
                              str(heap[e.compile(bindings)]) for e in self.value]))

expression = Forward()
operand = array | identifier | real | integer

class Operator(BaseElement, Immediate): pass
operator = oneOf('+ - * / ^').setParseClass(Operator, True)

class ComparisonOperator(BaseElement, Immediate): pass
comparisonOperator = oneOf('< <= > >= ==').setParseClass(ComparisonOperator, True)

class BooleanOperator(BaseElement, Immediate): pass
booleanOperator = oneOf('and or xor').setParseClass(BooleanOperator, True)

class Func(namedtuple("Func", ['name', 'expression']), HasIteratedVariables):
    def getIteratedVariableNames(self):
        return self.expression.getIteratedVariableNames()

    def compile(self, bindings):
        return self.name + '(' + self.expression.compile(bindings) + ')'

func = (oneOf('exp log d') + Suppress('(') + expression + Suppress(')')).setParseClass(Func, True)

atom =  func | '(' + expression + ')' | operand
expression << atom + ZeroOrMore((operator | comparisonOperator | booleanOperator) + atom)
expression = expression.setParseClass(Expression)

# An Equation is made of two Expressions separated by an equal sign
class Equation(namedtuple("Equation", ['lhs', 'rhs']), HasIteratedVariables):
    def getIteratedVariableNames(self):
        return self.lhs.getIteratedVariableNames() + self.rhs.getIteratedVariableNames()

    def compile(self, bindings):
        return self.lhs.compile(bindings) + ' = ' + self.rhs.compile(bindings)

equation = (expression + Suppress('=') + expression).setParseClass(Equation, True)

class Condition(namedtuple("Condition", ["expression"]), HasIteratedVariables):
    def getIteratedVariableNames(self):
        return self.expression.getIteratedVariableNames()

    def evaluate(self, bindings, heap):
        return self.expression.evaluate(bindings, heap)

condition = (Suppress(Keyword('if')) + expression).setParseClass(Condition, True)

# A Lst is a sequence of space-delimited strings (usually numbers), used for an iterator
# e.g. 01 02 03 04 05 06
Lst = namedtuple("Lst", ['value'])
lst = OneOrMore(Word(alphanums)).setParseClass(Lst)

# An Iterator is the combination of a VariableName and a Lst
# Each occurence of the VariableName inside an Index or a Placeholder will be replaced
# with each value in the Lst, sequentially, at the compile stage
# e.g. com in 01 02 03 04 05 06 07 08 09
class Iter(namedtuple("Iter", ['variableName', 'lst'])):
    # Return lst
    def compile(self):
        return {self.variableName: self.lst.value}

iter = (variableName + Suppress(Keyword('in')) + (lst | variableName)).setParseClass(Iter, True)

# A Formula is the combination of an equation and of one or more Iter(ators)
# This is the full form of the code passed from eViews to the compiler
# e.g. {V}[com] = {V}D[com] + {V}M[com], V in Q CH G I DS, com in 01 02 03 04 05 06 07 08 09
class Formula(namedtuple("Formula", ['equation', 'conditions', 'iterators'])):
    def compile(self, heap):
        # Find the unique variableNames used as Placeholders or Indexes
        uniqueVars = set(self.equation.getIteratedVariableNames())
        # Compile each iterator to get a dict of {VariableNames: Iter}
        iterators = dict(itertools.chain(*[i.compile().items() for i in self.iterators]))

        # Check that each iterator is defined only once
        iterVariables = [i.variableName for i in self.iterators]
        if len(iterVariables) > len(set(iterVariables)):
            raise NameError("Some iterated variables are defined multiple times")

        # Check that all VariableNames used as iterators in the equation are defined
        # in the iterators section of the Formula
        missingVars = uniqueVars - set(iterators.keys())
        if len(missingVars) > 0:
            raise IndexError("This iterated variables are not defined: " + ", ".join([e.value for e in missingVars]))

        # Cartesian product of all iterators, returned as dicts
        # Turns {'V': ['Q', 'X'], 'com': ['01', '02', '03']}
        # into [{'V': 'Q', 'com': '01'}, {'V': 'Q', 'com': '02'}, {'V': 'Q', 'com': '03'},
        #       {'X': 'Q', 'com': '01'}, {'X': 'Q', 'com': '02'}, {'X': 'Q', 'com': '03'} ]
        cartesianProduct = [l for l in apply(itertools.product, iterators.values())]
        iteratorDicts = [dict(zip(iterators.keys(), p)) for p in cartesianProduct]

        # Evaluate the condition for each iterator binding
        if len(self.conditions) > 0:
            if len(self.iterators) > 0:
                conditions = [self.conditions[0].evaluate(bindings, heap) for bindings in iteratorDicts]
            else:
                conditions = [self.conditions[0].evaluate({}, heap)]
        else:
            if len(self.iterators) > 0:
                conditions = [True] * len(iteratorDicts)
            else:
                conditions = [True]

        return "\n".join([self.equation.compile(bindings) for condition, bindings in zip(conditions, iteratorDicts) if condition])

formula = (equation +
           Group(Optional(condition)) +
           Group(Optional(Suppress(',') + delimitedList(iter)))).setParseClass(Formula, True)
