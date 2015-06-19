import plyyacc

def build_variable(name):
    ('VarName', (('VarId', (name,)), None, None))

def extract_varnames(expr):
    if expr[0] == 'VarName':
        return (expr, )
    elif expr[0] == 'ExprBinary':
        return extract_varnames(expr[2]) + extract_varnames(expr[3])
    elif expr[0] == 'ExprGroup':
        return extract_varnames(expr[1])
    elif expr[0] == 'FunctionCallArgs':
        return extract_varnames(expr[2])
    elif expr[0] == 'QualifiedExprList':
        return tuple(extract_varnames(e) for e in expr[2])
    elif expr[0] == 'Qualified':
        return extract_varnames(expr[0])
    elif expr[0] == 'EquationDef':
        return extract_varnames(expr[2]) + extract_varnames(expr[3])
    else:
        return ()

# def get_iterators_in_expr(expr, heap):
#     if expr[0] == 'VarName':


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


if __name__ == "__main__":
    compile("""%test := {"15", "05"}
               test = X|O|[1, c]{t-1}
            """, {})
    # print plyyacc.parser.parse("""test = X|O|[1, 2]{t-1} if test > 2 where i in %c
    #                       %test := {"15", "05"}
    #                       functionTest = function()
    #                       functionTest2 = function(hello[c] where (c, s) in ({"01"}, {"05"}), world)
    #                       """)
