from functools import wraps
import itertools

def traverse(func):
    def wrapped_func(ast):
        try:
            ret = func(ast)
        except TypeError:
             # func doesn't take care of terminals
            return iter([])
        else:
            if ret is not None:
                return ret
            else:
                return traverse_with_wrapped_func(ast)

    @wraps(func)
    def traverse_with_wrapped_func(ast):
        try:
            # The func may return directly on the node
            ret = func(ast)
            if ret:
                return ret
            else:
                if ast[0] == 'VarName':
                    return itertools.chain(wrapped_func(ast[1]), wrapped_func(ast[2]), wrapped_func(ast[3]))
                elif ast[0] == 'VarId':
                    return itertools.chain.from_iterable(wrapped_func(a) for a in ast[1])
                elif ast[0] == 'Index':
                    return wrapped_func(ast[1])
                elif ast[0] == 'IteratorList':
                    return itertools.chain.from_iterable(wrapped_func(a) for a in ast[1])
                elif ast[0] == 'ExprList':
                    return itertools.chain.from_iterable(wrapped_func(a) for a in ast[1])
                elif ast[0] == 'ExprBinary':
                    return itertools.chain(wrapped_func(ast[2]), wrapped_func(ast[3]))
                elif ast[0] == 'ExprGroup':
                    return wrapped_func(ast[1])
                elif ast[0] == 'FunctionCall':
                    return wrapped_func(ast[2])
                elif ast[0] == 'Placeholder':
                    return wrapped_func(ast[1])
                elif ast[0] == 'QualifiedExprList':
                    return itertools.chain.from_iterable(wrapped_func(a) for a in ast[1])
                elif ast[0] == 'Qualified':
                    return itertools.chain(wrapped_func(ast[1]), wrapped_func(ast[2]), wrapped_func(ast[3]))
                elif ast[0] == 'EquationDef':
                    return (wrapped_func(ast[2]), wrapped_func(ast[3]))
                else:
                    return iter([])
        # Terminals (ints, floats, etc.) are not iterable
        except TypeError:
            return iter([])

    return traverse_with_wrapped_func


def transform(func):
    def wrapped_func(self, ast, *args):
        try:
            ret = func(self, ast, *args)
        except TypeError:
             # func doesn't take care of terminals
            return ast
        else:
            if ret is not None:
                return ret
            else:
                return transform_with_wrapped_func(self, ast, *args)

    @wraps(func)
    def transform_with_wrapped_func(self, ast, *args):
        # The func may return directly on the node
        ret = func(self, ast, *args)
        if ret:
            return ret
        else:
            if ast[0] == 'VarName':
                return ('VarName', wrapped_func(self, ast[1], *args), wrapped_func(self, ast[2], *args), wrapped_func(self, ast[3], *args))
            elif ast[0] == 'VarId':
                return ('VarId', [wrapped_func(self, a, *args) for a in ast[1]])
            elif ast[0] == 'Index':
                return ('Index', wrapped_func(self, ast[1], *args))
            elif ast[0] == 'ExprList':
                return ('ExprList', [wrapped_func(self, a, *args) for a in ast[1]])
            elif ast[0] == 'ExprBinary':
                return ('ExprBinary', ast[1], wrapped_func(self, ast[2], *args), wrapped_func(self, ast[3], *args))
            elif ast[0] == 'ExprGroup':
                return ('ExprGroup', wrapped_func(self, ast[1], *args))
            elif ast[0] == 'FunctionCall':
                return ('FunctionCall', ast[1], wrapped_func(self, ast[2], *args))
            elif ast[0] == 'Placeholder':
                return ('Placeholder', wrapped_func(self, ast[1], *args))
            elif ast[0] == 'QualifiedExprList':
                return ('QualifiedExprList', [wrapped_func(self, a, *args) for a in ast[1]])
            elif ast[0] == 'Qualified':
                return ('Qualified', wrapped_func(self, ast[1], *args), wrapped_func(self, ast[2], *args), wrapped_func(self, ast[3], *args))
            elif ast[0] == 'EquationDef':
                return ('EquationDef', wrapped_func(self, ast[2], *args), wrapped_func(self, ast[3], *args))
            else:
                return ast

    return transform_with_wrapped_func


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
    # Shortcut for qualified expressions: only look within the expression
    elif expr[0] = 'Qualified':
        return extract_iterators(expr[1])
    # Don't consider iterators that are inside functions from the outside
    elif expr[0] == 'FunctionCall':
        return iter([])
        # # Extract the whereClauses of the function's arguments, if any
        # whereClauses = (qualifiedExpr[3] for qualifiedExpr in expr[2] if qualifiedExpr[3])
        # return itertools.chain.from_iterable(extract_iterators(w) for w in whereClauses)
    elif expr[0] == 'WhereIdList':
        return expr[1]
    elif expr[0] == 'IteratorSetLiteral':
        return expr[1]
    elif expr[0] == 'IteratorLocal':
        return expr[1]
    elif expr[0] == 'IteratorParallelSet':
        return expr[1][1]
    elif expr[0] == 'IteratorParallelSetLocal':
        return expr[1][1]


def build_variable(name):
    ('VarName', ('VarId', (name,)), None, None)
