import lexer

class Compiler:
    def __init__(self, file):
        self.lexer = lexer.Lexer(file)
        self.heap = {}
        # Init tokens
        self.token = self.lexer.read()
        self.nextToken = self.lexer.read()
        self.Instruction()

    def advance(self):
        self.token = self.nextToken
        self.nextToken = self.lexer.read()

    def match(self, tokenType):
        if self.token[0] == tokenType:
            self.advance()
        else:
            self.expected(tokenType)

    def read(self, tokenType):
        if self.token[0] == tokenType:
            ret = self.token[1]
            self.advance()
            return ret
        else:
            self.expected(tokenType)

    def expected(self, tokenType):
        raise SyntaxError("Syntax error: Expected {0}".format(tokenType))

    def readList(self, term):
        """
        <list> ::= (<integer> | <name>)*
        """
        ret = []
        while self.token[0] <> term:
            if self.token[0] == "integer" or self.token[0] == "name":
                ret.append(self.token[1])
                self.advance()
            else:
                self.expected("integer or string")
        return ret

    def Instruction(self):
        """
        <instruction> ::= <assignment> | <include> | <iter> | <formula>
        """
        if self.token[0] == 'local':
            self.Assignment()
        elif self.token[0] == 'include':
            self.Include()
        elif self.nextToken[1] == "in":
            self.Iter()
        else:
            self.Formula()

    def Assignment(self):
        """
        <assignment> ::= <localName> ":=" <list>
        """
        local = self.read('local')
        self.match('assign')
        list = self.readList('newline')
        self.heap[local] = list

    def Formula(self):
        """
        <formula> ::= <expression> "=" <expression> [ (<iter>)* ]
        """
        local = self.read('local')
        self.match('assign')
        list = self.readList('newline')
        self.heap[local] = list
