from collections import *
from pyparsing import *
from funcy import *

def tokensAsList(kls, tokens):
    return kls(tokens.asList())

def tokensAsArguments(kls, tokens):
    return kls(*tokens.asList())

def setParseClass(self, kls, unpack = False):
    self.setParseAction(partial(tokensAsArguments if unpack else tokensAsList, kls))
    return self

ParserElement.setParseClass = setParseClass

# A VariableName must start with an alphabetical character or an underscore,
# and can contain any number of alphanumerical characters or underscores
VariableName = namedtuple("VariableName", ['value'])
variableName = Word(alphas + '_', alphanums + '_').setParseClass(VariableName, True)

# A Placeholder is a VariableName enclosed in curly brackets, e.g. `{X}`
Placeholder = namedtuple("Placeholder", ['value'])
placeholder = (Suppress('{') + variableName + Suppress('}')).setParseClass(Placeholder, True)

# An identifier is a combination of one or more VariableNames and Placeholders
# e.g. {V}_energy, or Price{O}
Identifier = namedtuple("Identifier", ['value'])
identifier = ( (variableName | placeholder) + ZeroOrMore(variableName | placeholder) ).setParseClass(Identifier)

code = "testVar{X}"

print identifier.parseString(code)
