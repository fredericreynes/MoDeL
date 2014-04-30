import lexer

class DefaultGenerator:
    @staticmethod
    def index(components):
        return '_' + '_'.join(components)

class Compiler:
    def __init__(self, file, generator = DefaultGenerator):
        self.tokens = self.lex_all(file)
        self.tokens.append((None, ''))
        self.heap = {}
        self.generator = generator
        # Init tokens
        self.seek_token(0)
        self.Instruction()

    def lex_all(self, file):
        lex = lexer.Lexer(file)
        tokens = [lex.read()]
        tok = tokens[0]
        while tok[0] <> None:
            tok = lex.read()
            tokens.append(tok)
        return tokens

    def seek_token(self, tok_pos):
        self.tok_pos = tok_pos
        self.token = self.tokens[tok_pos]
        self.next_token = self.tokens[tok_pos + 1]

    def advance(self):
        self.seek_token(self.tok_pos + 1)

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
        elif self.next_token[1] == "in":
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
        <expression> ::= <term> (<operator> <term>)*
        """
        all_terms = []
        all_iterators = set()
        all_identifiers = []

        if not self.isTerm():
            self.expected('term')

        while self.isTerm() or self.token[0] == 'operator':
            if self.token[0] == 'operator':
                all_terms.append(self.read('operator'))
            else:
                compiled, iterators, identifiers = self.readTerm()
                all_terms.append(compiled)
                all_iterators.update(iterators)
                all_identifiers.append(identifiers)

        return (' '.join(all_terms),
                all_iterators,
                all_identifiers)

    def isTerm(self):
        return self.token[0] == 'name' or self.token[0] == 'pipe' or self.token[0] == 'lparen' or self.token[0] == 'local' or self.token[0] == 'counter' or self.token[0] == 'real' or self.token[0] == 'integer'

    def readFunction(self):


    def readTerm(self):
        """
        <term> ::= <function> | <lparen> <expression> <rparen> | <local> | <counter> | <real> | <integer> | <identifier>
        """
        iterators = set()
        identifiers = set()

        if self.token[0] == 'name' and self.next_token[0] == 'lparen':
            compiled, iterators, identifiers = self.readFunction()
        elif self.token[0] == 'lparen':
            self.match('lparen')
            compiled, iterators, identifiers = self.readExpression()
            self.match('rparen')
        elif self.token[0] == 'local':
            compiled = "%({0})s".format(self.read('local'))
        elif self.token[0] == 'counter':
            compiled = self.read('counter')
            iterators.add(compiled)
            compiled = "%({0})s".format(compiled)
        elif self.token[0] == 'real':
            compiled = self.read('real')
        elif self.token[0] == 'integer':
            compiled = self.read('integer')
        else:
            compiled, iterators = self.readIdentifier()
            identifiers = compiled

        return (compiled, iterators, identifiers)

    def readIdentifier(self):
        """
        <identifier> ::= (<name> | <placeholder>)+ [<index>] [<time>]
        """
        components = []
        iterators = set()

        if not self.token[0] in ['name', 'pipe']:
            self.expected('name or placeholder')

        while self.token[0] in ['name', 'pipe']:
            if self.token[0] == 'name':
                components.append(self.read('name'))
            elif self.token[0] == 'pipe':
                placeholder = self.readPlaceholder()
                components.append(placeholder[0])
                iterators.add(placeholder[1])

        if self.token[0] == 'lbracket':
            index, index_iterators = self.readIndex()
            components.append(index)
            iterators.update(index_iterators)

        if self.token[0] == 'lcurly':
            time = self.readTime()

        return (''.join(components), iterators)


    def readPlaceholder(self):
        """
        <placeholder> ::= <pipe> <name> <pipe>
        """
        self.match('pipe')
        name = self.read('name')
        self.match('pipe')
        return ("%({0})s".format(name), name)

    def readIndex(self):
        """
        <index> ::= <lbracket> (<name> | <integer>) (<comma> (<name> | <integer>))+ <rbracket>
        """
        components = []
        iterators = set()

        self.match('lbracket')

        if self.token[0] == 'name':
            name = self.read('name')
            components.append("%({0})s".format(name))
            iterators.add(name)
        elif self.token[0] == 'integer':
            components.append(self.read('integer'))
        else:
            self.expected('iterator name or integer')

        while self.token[0] == 'comma':
            self.match('comma')
            if self.token[0] == 'name':
                name = self.read('name')
                components.append("%({0})s".format(name))
                iterators.add(name)
            elif self.token[0] == 'integer':
                components.append(self.read('integer'))
            else:
                self.expected('iterator name or integer')

        self.match('rbracket')
        return (self.generator.index(components), iterators)

    def readFormula(self):
        """
        <formula> ::= <expression> <equal> <expression> [ (<iter>)* ]
        """
        lhs = self.readExpression()
        self.match('equal')
        rhs = self.readExpression()

        print lhs, rhs
