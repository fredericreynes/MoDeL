from functools import wraps
import itertools
import plyyacc

def build_variable(name):
    ('VarName', ('VarId', (name,)), None, None)

def traverse(func):
    def wrapped_func(ast):
        try:
            ret = func(ast)
        except TypeError:
             # func doesn't take care of terminals
            return ()
        else:
            if ret is not None:
                return ret
            else:
                return traverse_with_wrapped_func(ast)

    @wraps(func)
    def traverse_with_wrapped_func(ast):
        if ast[0] == 'VarName':
            return wrapped_func(ast[1]) + wrapped_func(ast[2]) + wrapped_func(ast[3])
        elif ast[0] == 'VarId':
            return tuple(itertools.chain.from_iterable(wrapped_func(a) for a in ast[1]))
        elif ast[0] == 'Placeholder':
            return wrapped_func(ast[1])
        elif ast[0] == 'Index':
            return wrapped_func(ast[1])
        elif ast[0] == 'ExprList':
            return tuple(itertools.chain.from_iterable(wrapped_func(a) for a in ast[1]))
        elif ast[0] == 'ExprBinary':
            return wrapped_func(ast[2]) + wrapped_func(ast[3])
        elif ast[0] == 'ExprGroup':
            return wrapped_func(ast[1])
        elif ast[0] == 'FunctionCallArgs':
            return wrapped_func(ast[2])
        elif ast[0] == 'QualifiedExprList':
            return tuple(itertools.chain.from_iterable(wrapped_func(a) for a in ast[1]))
        elif ast[0] == 'Qualified':
            return wrapped_func(ast[1]) + wrapped_func(ast[2]) + wrapped_func(ast[3])
        elif ast[0] == 'EquationDef':
            return wrapped_func(ast[2]) + wrapped_func(ast[3])
        else:
            return ()

    return traverse_with_wrapped_func


@traverse
def extract_varnames(expr):
    if expr[0] == 'VarName':
        return (expr, )

@traverse
def extract_simple_varids(expr):
    if expr[0] == 'VarId' and len(expr[1]) == 1 and isinstance(expr[1][0], basestring):
        return expr[1]

@traverse
def extract_iterators(expr):
    if expr[0] == 'Index':
        return extract_simple_varids(expr[1])
    elif expr[0] == 'Placeholder':
        return expr[1]


# Given a tuple of dicts, returns a single merged dict
def merge_dicts(dicts):
    ret = {}
    for d in dicts:
        ret.update(d)
    return ret

class CompilerError(Exception):
    pass

class Compiler:
    def error(self, msg):
        raise CompilerError("Error at line %s.\n\n%s\n\n%s\n" % (self.current_line, self.lines[self.current_line - 1], msg))

    def get_if_exists(self, key, hsh, msg):
        if key in hsh:
            return hsh[key]
        else:
            self.error("%s `%s` is not defined." % (msg, key))


    # Set
    # ('SetLiteral', tuple)
    #
    def compile_set(self, ast):
        if ast[0] == 'SetLiteral':
            return zip(ast[1], range(1, len(ast[1]) + 1))


    # Expressions
    #
    def compile_expression(self, ast, iterators, parallel_iterator_names):
        # Find iterators used in this expression
        iterator_names = set(extract_iterators(ast))

        # Only keep the iterators we need in this expression

        # First get all parallel iterators, if any
        parallel_iterators = []
        if len(parallel_iterator_names) > 0:
            try:
                parallel_iterators = [ iterators[k] for k in parallel_iterator_names ]
            except KeyError as e:
                self.error("Undefined iterator `%s` is used in expression." % e.args)
            # Check that all parallel iterators have the same number of elements
            ref_len = len(parallel_iterators[0])
            if not all(len(iter) == ref_len for iter in parallel_iterators):
                self.error("Parallel iterators %s differ in length." % str(parallel_iterator_names))
            parallel_iterators = (merge_dicts(dicts) for dicts in itertools.izip(*parallel_iterators))

        # Then, get the other, non-parallel, iterators we need
        try:
            other_iterators = [ iterators[k] for k in iterator_names.difference(parallel_iterator_names) ]
        except KeyError as e:
            self.error("Undefined iterator `%s` is used in expression." % e.args)
        iterators = (merge_dicts(dicts) for dicts in itertools.product(parallel_iterators, *other_iterators))
        print "Final iterators", list(iterators)

    # From an iterator name `i` and its elements [i1, i2, ...], builds a list of dicts:
    # [ {'i': i1, '$i': 1}, {'i': i2, '$i': 2}, ... ]
    #
    def build_iterator(self, name, elements):
        index_name = "$%s" % name
        return [ {name: e[0], index_name: e[1]} for e in elements ]

    # Iterators
    # Each iterator can be one of:
    # - ('IteratorSetLiteral', ID, set)
    # - ('IteratorLocal', ID, localId)
    # - ('IteratorParallelSet', idGroup, setGroup)
    # - ('IteratorParallelLocal', idGroup, localGroup)
    #
    def compile_iterator(self, ast):
        local_iterators = {}
        parallel_iterator_names = []

        if ast[0] == 'IteratorLocal':
            local_iterators = { ast[1]: self.build_iterator(ast[1], self.get_if_exists(ast[2], self.heap, "Local variable")) }
        elif ast[0] == 'IteratorSetLiteral':
            local_iterators = { ast[1]: self.build_iterator(ast[1], self.compile_set(ast[2])) }
        elif ast[0] == 'IteratorParallelSet':
            local_iterators = { e[0]: self.build_iterator(e[0], e[1]) for e in zip(ast[1][1], (self.compile_set(l) for l in ast[2][1])) }
            parallel_iterator_names = ast[1][1]

        return local_iterators, parallel_iterator_names



    # whereClause
    # ('Where', iteratorList)
    #
    def compile_whereClause(self, ast):
        iterator_list = ast[1][1]
        local_iterators = {}
        parallel_iterator_names = []

        for iter in iterator_list:
            ret = self.compile_iterator(iter)
            local_iterators.update(ret[0])
            parallel_iterator_names.extend(ret[1])

        print local_iterators, parallel_iterator_names
        return local_iterators, set(parallel_iterator_names)

    # Qualified Expressions
    # ('Qualified', expr, ifClause, whereClause)
    #
    def compile_qualified(self, ast, iterators):
        # Compile whereClause to add explicit iterators, if any
        if not ast[3] is None:
            local_iterators, parallel_iterator_names = self.compile_whereClause(ast[3])
            iterators.update( local_iterators )

        # Compile ifClause, if any

        # Compile expr
        self.compile_expression(ast[1], iterators, parallel_iterator_names)

    def compile(self, program):
        self.heap = {}
        self.iterators = {'test': ['01', '02', '99']}
        self.lines = program.split('\n')
        self.current_line = 0

        # Parse the program
        ast = plyyacc.parser.parse(program)

        # Check for errors
        if len(plyyacc.errors) == 0:
            print ast, "\n"

            try:
                # Go through each statement
                for a in ast[1]:
                    s = a[1]
                    self.current_line = a[2]

                    if s[0] == 'EquationDef':
                        self.compile_qualified(s[3], self.iterators)
            except CompilerError as e:
                print e

        else:
            for e in plyyacc.errors:
                self.current_line = e[1]
                self.error(e[0])


def compile(program, heap):
    print "Compiling:\n", program
    ast = plyyacc.parser.parse(program)
    print ast, "\n"

    # Go through statements
    for a in ast[1]:
        # Extract statement
        s = a[1]
        self.current_line = a[2]

        # if s[0] == 'LocalDef':
        #     heap[s[1]] = s[2][1]
        #     #print heap

        if s[0] == 'EquationDef':
            # Identify iterators
            print(extract_varnames(s))
            print(extract_iterators(s))


def test():
    # compile("""%test := {"15", "05"}
    # test = X|O|[42, c]{t-1}
    # """, {})
    compiler = Compiler()
    compiler.compile("""V = x[c] where c in {'01', '02'}
    test = X|O|[s] where (O, V) in ({'D', 'M'}, {'X', 'IA'}), s in {'14', '15', '16'}\n""")

if __name__ == "__main__":
    test()
    # import timeit
    # print(timeit.timeit('test()', setup="from __main__ import test", number=3000)/3000)
    # print plyyacc.parser.parse("""test = X|O|[1, 2]{t-1} if test > 2 where i in %c
    #                       %test := {"15", "05"}
    #                       functionTest = function()
    #                       functionTest2 = function(hello[c] where (c, s) in ({"01"}, {"05"}), world)
    #                       """)
