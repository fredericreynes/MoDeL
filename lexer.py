from plex import *
from StringIO import StringIO

class Lexer(Scanner):
    digit = Range("09")
    integer = Rep1(digit)


    lexicon = Lexicon([ (integer, 'int') ])

    def __init__(self, file):
        Scanner.__init__(self, self.lexicon, file)


lexer = Lexer(StringIO("56"))
print lexer.read()
