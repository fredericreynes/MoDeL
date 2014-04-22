from plex import *
from StringIO import StringIO

class Lexer(Scanner):
    digit = Range("09")
    integer = Opt(Str('-')) + Rep1(digit)
    real = Opt(Str('-')) + Rep1(digit) + Str('.') + Rep1(digit)

    arithmetics = Any("+-*/^")
    comparisons = Str("<>", "<", "<=", "=<", ">", ">=", "=>", "==")
    booleans = Str("and", "or", "xor")
    operators = arithmetics | comparisons | booleans
    equal = Str("=")
    assign = Str(":=")

    alpha = NoCase(Range("az"))
    name = Rep1(Any("@_") | alpha | digit)
    local_name = Str("%") + name


    keywords = Str("if", "where", "on", "in", "include")
    space = Any(" \t")

    lexicon = Lexicon([
        (integer, 'integer'),
        (real, 'real'),
        (operators, 'operator'),
        (equal, 'equal'),
        (assign, 'assign'),
        (name, 'name'),
        (local_name, 'local'),
        (Str('('), 'lparen'),
        (Str(')'), 'rparen'),
        (Str('['), 'lbracket'),
        (Str(']'), 'rbracket'),
        (Str('{'), 'lcurly'),
        (Str('}'), 'rcurly'),
        (Str('|'), 'pipe'),
        (space, IGNORE)
    ])

    def read_all(self):
        ret = []
        token = self.read()
        while not (token[0] is None):
            ret.append(token)
            token = self.read()
        return ret

    def __init__(self, file):
        Scanner.__init__(self, self.lexicon, file)

# print Lexer(StringIO("PRF[sm]{-1}")).read_all()
