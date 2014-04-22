from plex import *
from StringIO import StringIO

class Lexer(Scanner):
    digit = Range("09")
    int = Rep1(digit)
    real = Rep1(digit) + Str('.') + Rep1(digit)


    lexicon = Lexicon([
        (int, 'int'),
        (real, 'real'),
    ])

    def __init__(self, file):
        Scanner.__init__(self, self.lexicon, file)


lexer = Lexer(StringIO("50"))
print lexer.read()
