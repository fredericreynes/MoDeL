from plex import *
from StringIO import StringIO

class Lexer(Scanner):
    digit = Range("09")
    integer = Opt(Str('-')) + Rep1(digit)
    real = Opt(Str('-')) + Rep1(digit) + Str('.') + Rep1(digit)
    operators = Any("+-*/")
    alpha = NoCase(Range("az"))
    name = Rep1(Any("@_") | alpha | digit)
    local_name = Str("%") + name

    space = Any(" \t\n")

    lexicon = Lexicon([
        (integer, 'integer'),
        (real, 'real'),
        (operators, 'operator'),
        (name, 'name'),
        (local_name, 'local'),
        (Str('('), 'lparen'),
        (Str(')'), 'rparen'),
        (Str('['), 'lbracket'),
        (Str(']'), 'rbracket'),
        (Str('{'), 'lcurly'),
        (Str('}'), 'rcurly'),
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
