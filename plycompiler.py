from functools import wraps
import plyyacc

def build_variable(name):
    ('VarName', ('VarId', (name,)), None, None)

def traverse(func):
    def wrapped_func(ast):
        try:
            ret = func(ast)
        except TypeError:
             # func doesn't take care of terminals
            if ast is None:
                return ()
            elif isinstance(ast, int):
                return ast
            elif isinstance(ast, string):
                return ast
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
            return tuple(wrapped_func(a) for a in ast[1])
        elif ast[0] == 'Placeholder':
            return wrapped_func(ast[1])
        elif ast[0] == 'Index':
            return wrapped_func(ast[1])
        elif ast[0] == 'ExprList':
            return tuple(wrapped_func(a) for a in ast[1])
        elif ast[0] == 'ExprBinary':
            return wrapped_func(ast[2]) + wrapped_func(ast[3])
        elif ast[0] == 'ExprGroup':
            return wrapped_func(ast[1])
        elif ast[0] == 'FunctionCallArgs':
            return wrapped_func(ast[2])
        elif ast[0] == 'QualifiedExprList':
            return tuple(wrapped_func(a) for a in ast[1])
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
def extract_varids(expr):
    if expr[0] == 'VarId':
        return (expr, )

def compile(program, heap):
    ast = plyyacc.parser.parse(program)

    # Go through statements
    for a in ast[1]:
        s = a[1]

        if s[0] == 'LocalDef':
            heap[s[1]] = s[2][1]
            print heap

        elif s[0] == 'EquationDef':
            # Identify iterators
            print(extract_varnames(s))
            print(extract_varids(s))



def test():
    compile("""%test := {"15", "05"}
    test = X|O|[1, c]{t-1}
    """, {})

if __name__ == "__main__":
    test()
    # import timeit
    # print(timeit.timeit('test()', setup="from __main__ import test", number=3000))
    # print plyyacc.parser.parse("""test = X|O|[1, 2]{t-1} if test > 2 where i in %c
    #                       %test := {"15", "05"}
    #                       functionTest = function()
    #                       functionTest2 = function(hello[c] where (c, s) in ({"01"}, {"05"}), world)
    #                       """)
