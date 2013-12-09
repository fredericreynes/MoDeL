from collections import *
from pyparsing import *
from funcy import *

def tokensAsList(kls, tokens):
    print "Inside tokensAsList, with class {0}".format(kls.__name__)
    print "Result: {0}\n".format(kls(tokens.asList()))
    return kls(tokens.asList())

def tokensAsArguments(kls, tokens):
    return kls(*tokens.asList())

def setParseClass(self, kls):
    self.setParseAction(partial(tokensAsList if issubclass(kls, ListElement) else tokensAsArguments, kls))
    return self

ParserElement.setParseClass = setParseClass

class ListElement:
    def __init__(self, lst):
        self.lst = lst

    def __getitem__(self, i):
        return self.lst[i]

    def __str__(self):
        return self.__class__.__name__ + '[' + ', '.join([str(e) for e in self.lst]) + ']'


# A VariableName must start with an alphabetical character or an underscore,
# and can contain any number of alphanumerical characters or underscores
VariableName = namedtuple("VariableName", ['value'])
variableName = Word(alphas + '_', alphanums + '_').setParseClass(VariableName)

# A Placeholder is a VariableName enclosed in curly brackets, e.g. `{X}`
Placeholder = namedtuple("Placeholder", ['value'])
placeholder = (Suppress('{') + variableName + Suppress('}')).setParseClass(Placeholder)

# An Identifier is a combination of one or more VariableNames and Placeholders
# e.g. {V}_energy, or Price{O}
class Identifier(ListElement): pass
identifier = ( (variableName | placeholder) + ZeroOrMore(variableName | placeholder) ).setParseClass(Identifier)

# An Index is meant to be used in conjunction with an Array
# It can have multiple dimensions, e.g. [com, sec]
class Index(ListElement): pass
index = (Suppress('[') + delimitedList(variableName | nums) + Suppress(']')).setParseClass(Index)

class Array(ListElement): pass
array = (identifier + index).setParseClass(Array)

print array.parseString("pouet{X}_energy{O}[com, sec]")[0]
print Index([15, 90 ,8])
