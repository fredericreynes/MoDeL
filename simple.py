from simpleparse.common import numbers
from simpleparse.parser import Parser
from simpleparse.dispatchprocessor import *

declaration = open("simple.ebnf").read()

#class BaseProcessor(DispatchProcessor):
# Generic functions
def recursive(self, (tag,start,stop,subtags), buffer):
    return dispatchList(self, subtags, buffer)

def raw(self, (tag,start,stop,subtags), buffer):
    return buffer[start:stop]

def process(processorClass):
    processor = processorClass()
    def runProcessor(self, (tag,start,stop,subtags), buffer):
        return processor((tag,start,stop,subtags), buffer)
    return runProcessor



class BaseExpressionProcessor(DispatchProcessor):
    # Raw productions
    op = raw
    id = raw
    placeholder = raw
    unary_neg = raw
    series = raw
    number = raw

    # Recursive productions
    expr = recursive
    qualified = recursive
    paren_expr = recursive
    function = recursive

class ExtractSimpleIdentifier(BaseExpressionProcessor):
    index = recursive

    def series(self, (tag,start,stop,subtags), buffer):
        return raw(self, subtags[0][3][0], buffer)


class ExtractIterator(BaseExpressionProcessor):
    index = process(ExtractSimpleIdentifier)

    # def expr(self, (tag,start,stop,subtags), buffer):
    #     print multiMap(subtags).keys()

    def series(self, (tag,start,stop,subtags), buffer):
        # If there is one or more placeholders in the identifier

        # If there is an index
        if len(subtags) > 1:
            return self.index(subtags[1], buffer)

    def identifier(self, (tag,start,stop,subtags), buffer):
        parts = multiMap(subtags)
        if 'placeholder' in parts.keys():
            return parts['placeholder']
        else:
            return []


class EquationProcessor(BaseExpressionProcessor):
    # Recursive productions
    equation = recursive
    expr = process(ExtractIterator)


class TopProcessor(DispatchProcessor):
    hsh = {}

    expr = recursive
    series = recursive
    identifier = recursive
    index = recursive
    line = recursive

    op = raw
    id = raw
    unary_neg = raw
    symbol = raw
    local = raw
    number = raw
    comment = raw

    equation = process(EquationProcessor)

    def local_def(self, (tag,start,stop,subtags), buffer):
        local, set_lit = dispatchList(self, subtags, buffer)
        self.hsh[local] = set_lit
        print self.hsh

    def set_literal(self, (tag,start,stop,subtags), buffer):
        return dispatchList(self, subtags, buffer)




class TestParser(Parser):
    def buildProcessor(self):
        return TopProcessor()

class SimpleParser(Parser):
    pass

# success, ast, nextchar = parser.parse("test|g|[c, d]{1} > ( c)\n")
# success, ast, nextchar = parser.parse("test(t on f)\n")
#success, ast, nextchar = parser.parse("%test := {01, 02, 03}\n")
#success, ast, nextchar = parser.parse('+'.join(["test|O|[u, v] + pouet[c]"] * 250000) + "\n")

test = '''
test = (pouet + 2.0) - log(g[c, s])
#%sectors := {01, 02, 03}
# test
# test = world + 2
#%sectors := {01, 02, 03}
#%commodities := {coal, oil, elec, gas}
'''
success, ast, nextchar = TestParser(declaration, "main").parse(test)
import pprint
pprint.pprint(ast)

success, ast, nextchar = SimpleParser(declaration, "main").parse(test)

print "\nSimple parse\n"

#pprint.pprint(ast)
