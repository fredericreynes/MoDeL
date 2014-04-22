from plex import *
from tempfile import NamedTemporaryFile

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
    options = Str("@pv", "@over")

    continuation = Str('_') + Str('\n')
    newline = Str('\n') | Eof
    space = Any(" \t")

    lexicon = Lexicon([
        (integer, 'integer'),
        (real, 'real'),
        (operators, 'operator'),
        (equal, 'equal'),
        (assign, 'assign'),
        (keywords, 'keyword'),
        (options, 'option'),
        (name, 'name'),
        (local_name, 'local'),
        (Str('('), 'lparen'),
        (Str(')'), 'rparen'),
        (Str('['), 'lbracket'),
        (Str(']'), 'rbracket'),
        (Str('{'), 'lcurly'),
        (Str('}'), 'rcurly'),
        (Str('|'), 'pipe'),
        (Str(','), 'comma'),
        (newline, 'newline'),
        (space | continuation, IGNORE)
    ])

    def __init__(self, file):
        Scanner.__init__(self, self.lexicon, file)


#lex = Lexer(StringIO("@pv VA = sum(VA[s] on s)"))
f = NamedTemporaryFile(delete = False)
f.write("@pv VA = sum(VA[s] on s)")
f.close()
print repr(open(f.name, 'rb').read())
lex = Lexer(open(f.name, 'rU'))
tok = lex.read()
while tok[0] <> None:
    print tok
    tok = lex.read()
