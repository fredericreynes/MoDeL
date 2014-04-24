import lexer

class DefaultGenerator:
    def self.index(self, expressions):
        return '_' + '_'.join(expressions)

class Compiler:
    def __init__(self, file, generator = DefaultGenerator):
        self.lexer = lexer.Lexer(file)
        self.heap = {}
        self.generator = generator
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
        raise SyntaxError("Expected {0}".format(tokenType))

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
            self.readAssignment()
        elif self.token[0] == 'include':
            self.Include()
        elif self.nextToken[1] == "in":
            self.Iter()
        else:
            self.readFormula()

    def readAssignment(self):
        """
        <assignment> ::= <localName> ":=" <list>
        """
        local = self.read('local')
        self.match('assign')
        list = self.readList('newline')
        self.heap[local] = list

    def readExpression(self):
        """
        <expression> ::= <function> | <lparen> <expression> <rparen> | <term>
        """
        return self.readTerm()


    def readTerm(self):
        """
        <term> ::= <identifier> | <local> | <counter> | <real> | <integer>
        """
        return self.readIdentifier()


    def readIdentifier(self):
        """
        <identifier> ::= (<name> | <placeholder>)+ [<index>] [<time>]
        """
        components = []
        iterators = []

        if not self.token[0] in ['name', 'pipe']:
            self.expected('name or placeholder')

        while self.token[0] in ['name', 'pipe']:
            if self.token[0] == 'name':
                components.append(self.read('name'))
            elif self.token[0] == 'pipe':
                placeholder = self.readPlaceholder()
                iterators.append(placeholder)
                components.append(placeholder)

        if self.token[0] == 'lbracket':
            index = self.readIndex()

        if self.token[0] == 'lcurly':
            time = self.readTime()


    def readPlaceholder(self):
        """
        <placeholder> ::= <pipe> <name> <pipe>
        """
        self.match('pipe')
        name = self.read('name')
        self.match('pipe')
        return name

    def readIndex(self):
        """
        <index> ::= <lbracket> <expression> (<comma> <expression>)+ <rbracket>
        """
        self.match('lbracket')
        expression = self.readExpression()
        self.match('rbracket')
        return expression

    def readFormula(self):
        """
        <formula> ::= <expression> <equal> <expression> [ (<iter>)* ]
        """
        lhs = self.readExpression()
        self.match('equal')
        rhs = self.readExpression()
