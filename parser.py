import lexer
import itertools

class DefaultGenerator:
    @staticmethod
    def index(components):
        return '_' + '_'.join(components)

    @staticmethod
    def format_name(name):
        return "%({0})s".format(name)


class Compiler:
    def __init__(self, file, generator = DefaultGenerator, heap = None, iterators = None):
        self.tokens = self.lex_all(file)
        self.tokens.append((None, ''))

        if heap is None:
            self.heap = {}
        else:
            self.heap = heap

        if iterators is None:
            self.iterators = {}
        else:
            self.iterators = iterators

        self.generator = generator
        self.dependencies = {}
        # Init tokens
        self.seek_token(0)
        self.Instruction()

    @property
    def equations(self):
        return [l[0] for l in self.dependencies.values()]

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

    def fetch_in_heap(self, key):
        if not key in self.heap:
            raise NameError("Local variable {0} is used before having been declared.".format(key))
        return self.heap[key]

    def readList(self):
        """
        <list> ::= (<integer>* | <local>) [<backlash> (<integer>* | <local>)]
        """
        base_list = []
        if self.token[0] == "local":
            base_list = self.fetch_in_heap(self.read('local'))[0]
        elif self.token[0] == "integer":
            while self.token[0] == "integer":
                base_list.append(self.read('integer'))
        else:
            self.expected("integer or local variable name")

        excluded_list = []
        if self.token[0] == "backlash":
            self.advance()
            if self.token[0] == "local":
                excluded_list = self.fetch_in_heap(self.read('local'))[0]
            elif self.token[0] == "integer":
                while self.token[0] == "integer":
                    excluded_list.append(self.read('integer'))
            else:
                self.expected("integer or local variable name")

        return ([e for e in base_list if not e in excluded_list],
                [i for i, e in enumerate(base_list, 1) if e not in excluded_list])

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
            self.readFormula(self.readEquation)

    def readAssignment(self):
        """
        <assignment> ::= <localName> ":=" <list>
        """
        local = self.read('local')
        self.match('assign')
        list = self.readList()
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
                all_identifiers += identifiers

        return (' '.join(all_terms),
                all_iterators,
                all_identifiers)

    def isTerm(self):
        return self.token[0] == 'name' or self.token[0] == 'pipe' or self.token[0] == 'lparen' or self.token[0] == 'local' or self.token[0] == 'counter' or self.token[0] == 'real' or self.token[0] == 'integer'

    def readFunction(self):
        """
        <function> ::= <name> <lparen> (<expression> [<comma> <expression>]*) <rparen>
        """
        name = self.read('name')
        self.match('lparen')
        compiled, iterators, identifiers = self.readExpression()
        self.match('rparen')
        return ('{0}({1})').format(name, compiled), iterators, identifiers

    def readTerm(self):
        """
        <term> ::= <function> | <lparen> <expression> <rparen> | <local> | <counter> | <real> | <integer> | <identifier>
        """
        iterators = set()
        identifiers = []

        if self.token[0] == 'name' and self.next_token[0] == 'lparen':
            compiled, iterators, identifiers = self.readFunction()
        elif self.token[0] == 'lparen':
            self.match('lparen')
            compiled, iterators, identifiers = self.readExpression()
            self.match('rparen')
        elif self.token[0] == 'local':
            name = self.read('local')
            compiled = self.fetch_in_heap(name)
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
            identifiers = [compiled]

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

        while True:
            if self.token[0] == 'name':
                name = self.read('name')
                components.append(self.generator.format_name(name))
                iterators.add(name)
            elif self.token[0] == 'integer':
                components.append(self.read('integer'))
            else:
                self.expected('iterator name or integer')

            if self.token[0] == 'comma':
                self.match('comma')
            else:
                break

        self.match('rbracket')
        return (self.generator.index(components), iterators)

    def readIterator(self):
        """
        <iterator> ::= <name> "in" <list>
        """
        name = self.read('name')
        self.match('keyword')
        lists = self.readList()
        return [(name, lists[0]), ('$' + name, lists[1])]

    def readDelimitedList(self, reader):
        delimited_list = reader()
        while self.token[0] == 'comma':
            self.match('comma')
            delimited_list.extend(reader())
        return delimited_list

    def readEquation(self):
        """
        <equation> ::= <expression> <equal> <expression>
        """
        l_compiled, l_iterators, l_identifiers = self.readExpression()
        self.match('equal')
        r_compiled, r_iterators, r_identifiers = self.readExpression()
        return ('{0} = {1}'.format(l_compiled, r_compiled),
                l_iterators.union(r_iterators),
                l_identifiers + r_identifiers)


    def readFormula(self, reader):
        """
        <formula> ::= <equation> [ <if> <condition> ] [ (<where> | <on>) (<iter>)* ]
        """
        compiled, iterators, identifiers = reader()

        if self.token[0] == 'keyword' and self.token[1] == 'if':
            cond_compiled, cond_iterators, cond_identifiers = self.readCondition()

        local_iterators = {}
        if self.token[0] == 'keyword' and (self.token[1] == 'where' or self.token[1] == 'on'):
            self.match('keyword')
            local_iterators = dict(self.readDelimitedList(self.readIterator))

        # Merge global and local iterators
        local_iterators = dict(self.iterators.items() + local_iterators.items())

        # Cartesian product of all iterators
        # Check that all iterators been declared
        iter_names = list(iterators)
        for i in iter_names:
            if not i in local_iterators:
                raise NameError("Undefined iterator: {0}".format(i))

        # Cartesian product
        values = (local_iterators[i] for i in iter_names)
        product = list(itertools.product(*values))
        values = [dict(zip(iter_names, p)) for p in product]

        # Generate all equations, with their associated identifiers
        compiled = [compiled % v for v in values]
        identifiers = zip(*[[i % v for v in values] for i in identifiers])

        # print (compiled, iterators, identifiers)

        # Add the equations to the dependency graph
        for eq, ids in zip(compiled, identifiers):
            if ids[0] in self.dependencies:
                raise NameError("An equation for variable `{0}` has already been defined (`{1}`). Use the @over keyword to override the previous equation and use `{2}` instead.".format(ids[0], self.dependencies[ids[0]][0], eq))
            self.dependencies[ids[0]] = [eq, ids[1:]]
