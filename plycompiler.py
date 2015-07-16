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

class Compiler:
    def error(self, msg):
        print "Error at line %s.\n\n%s\n\n%s\n" % (self.current_line, self.lines[self.current_line], msg)

    def get_if_exists(self, key, hsh, msg):
        if key in hsh:
            return hsh[key]
        else:
            self.error("%s `%s` is not defined." % (msg, key))


    # Compile expressions
    #
    def compile_expression(self, ast, iterators):
        # Find iterators used in this expression
        iterator_names = extract_iterators(ast)

        # Get the corresponding lists
        for i in iterator_names:
            iterators.update({i: self.get_if_exists(i, iterators, "Iterator")})

            print iterators

    # Compile whereClause
    # ('Where', iterator)
    # iterator can be one of:
    # - ('IteratorImmediateList', ID, list)
    # - ('IteratorLocal', ID, localId)
    # IteratorLocal, IteratorParallelList, IteratorParallelLocal
    #
    def compile_whereClause(self, ast):
        iterator = ast[1]

        if iterator[0] == 'IteratorLocal':
            lst = self.get_if_exists(iterator[2], self.heap, "Local variable")
            return { iterator[1]: iter(lst) }
        elif iterator[0] == 'IteratorImmediateList':
            return { iterator[1]: iter(iterator[2]) }

    # Compile Qualified Expressions
    # ('Qualified', expr, ifClause, whereClause)
    #
    def compile_qualified(self, ast, iterators):
        # Compile whereClause to add explicit iterators, if any
        if not ast[3] is None:
            iterators.update( self.compile_whereClause(ast[3]) )

        # Compile ifClause, if any

        # Compile expr
        print iterators
        self.compile_expression(ast[1], iterators)

    def compile(self, program):
        self.heap = {}
        self.iterators = {}
        self.lines = program.split('\n')
        self.current_line = 0

        # Parse the program
        ast = plyyacc.parser.parse(program)

        # Go through each statement
        for a in ast[1]:
            s = a[1]

            if s[0] == 'EquationDef':
                self.compile_qualified(s[3], self.iterators)


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
    compiler.compile("""test = X|O| where O in {"D", "M"}\n""")

if __name__ == "__main__":
    test()
    # import timeit
    # print(timeit.timeit('test()', setup="from __main__ import test", number=3000)/3000)
    # print plyyacc.parser.parse("""test = X|O|[1, 2]{t-1} if test > 2 where i in %c
    #                       %test := {"15", "05"}
    #                       functionTest = function()
    #                       functionTest2 = function(hello[c] where (c, s) in ({"01"}, {"05"}), world)
    #                       """)
