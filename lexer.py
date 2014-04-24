from plex import *
from plex.traditional import re
from tempfile import NamedTemporaryFile
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
    string = Rep1(Any(".\\_@") | alpha | digit)
    local_name = Str("%") + name
    loop_counter = Str("$") + Rep1(alpha | digit)

    keywords = Str("if", "where", "on", "in", "include")
    options = Str("@pv", "@over")

    comment = Str('#') + Rep(AnyBut('\n'))
    continuation = Str('_') + Str('\n')
    newline = Rep1(Str('\n') | re("$"))
    space = Any(" \t")
    blank_line = Rep(space) + Opt(comment) + newline

    lexicon = Lexicon([
        (integer, 'integer'),
        (real, 'real'),
        (operators, 'operator'),
        (equal, 'equal'),
        (assign, 'assign'),
        (keywords, 'keyword'),
        (options, 'option'),
        (Str('\\'), 'backlash'),
        (name, 'name'),
        (string, 'string'),
        (local_name, 'local'),
        (loop_counter, 'counter'),
        (Str('('), 'lparen'),
        (Str(')'), 'rparen'),
        (Str('['), 'lbracket'),
        (Str(']'), 'rbracket'),
        (Str('{'), 'lcurly'),
        (Str('}'), 'rcurly'),
        (Str('|'), 'pipe'),
        (Str(','), 'comma'),
        (newline, 'newline'),
        (space | continuation | blank_line, IGNORE)
    ])

    def __init__(self, file):
        Scanner.__init__(self, self.lexicon, file)


# # test = """GDP = 0

# #         #Comment

# #         Another := 15 123
# #         """

# test = "01 02 03 04 \ 01 02"
# lex = Lexer(StringIO(test))

# # f = NamedTemporaryFile(delete = False)
# # f.write("@pv VA = sum(VA[s] on s)")
# # f.close()
# # # fw = open(f.name, 'a')
# # # fw.write('\n')
# # # fw.close()
# # f.name = "pouet.txt"
# # print repr(open(f.name, 'rb').read())
# # lex = Lexer(open(f.name, 'rU'))
# tok = lex.read()
# while tok[0] <> None:
#     print tok
#     tok = lex.read()
