import itertools
import plyyacc

import sys
import logger

from ast import *
from outputter import *

# Given a tuple of dicts, returns a single merged dict
def merge_dicts(dicts):
    ret = {}
    for d in dicts:
        ret.update(d)
    return ret


class CompilerError(Exception):
    pass

class Compiler:

    #
    # Compiler internals
    #
    # This is common to all Compiler versions,
    # and doesn't need to be modified by the external interface
    #

    def error(self, msg):
        raise CompilerError("Error at line %s.\n\n%s\n\n%s\n" % (self.current_line, self.lines[self.current_line - 1], msg))

    def get_if_exists(self, key, hsh, msg):
        if key in hsh:
            return hsh[key]
        else:
            self.error("%s `%s` is not defined." % (msg, key))

    #
    # AST transformations
    #

    # The value form of an expression is obtained
    # through an AST transform: every variable (Varname)
    # is turned into a product of PV * V
    @transform
    def ast_value(self, expr):
        if expr[0] == 'VarName':
            return ('ExprGroup', ('ExprBinary', '*', ('VarName', ('VarId', ['P'] + expr[1][1]), expr[2], expr[3]), expr))

    # Function calls are implement through as AST transformation:
    # the function call node is replaced with a node containing
    # the name of the function, and a list of compiled arguments
    # (which are just qualified expressions in the first)
    @transform
    def ast_functions(self, expr, iterators):
        # ('FunctionCall', name, qualifiedExprList)
        # For functions, only the iterators explicitly specified in the where clauses of the args are considered
        if expr[0] == 'FunctionCall':
            whereClauses = (arg[3] for arg in expr[2][1])
            explicit_iterator_names = set(itertools.chain(*(extract_iterators(w) for w in whereClauses)))
            return ('CompiledFunctionCall', expr[1], [self.compile_qualified(arg, iterators, explicit_iterator_names) for arg in expr[2][1]])


    # Set
    # ('SetLiteral', list, list)
    #
    def compile_set_literal(self, ast):
        if ast[0] == 'SetLiteral':
            return [e for e in zip(ast[1], range(1, len(ast[1]) + 1)) if e[0] not in ast[2] ]


    # From an iterator name `i` and its elements [(i1, 1), (i2, 2), ...], builds a list of dicts:
    # [ {'i': i1, '$i': 1}, {'i': i2, '$i': 2}, ... ]
    #
    def build_iterator(self, name, elements):
        index_name = '$' + name
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
            local_iterators = { ast[1]: self.build_iterator(ast[1], self.compile_set_literal(ast[2])) }
        elif ast[0] == 'IteratorParallelSet':
            local_iterators = { e[0]: self.build_iterator(e[0], e[1]) for e in zip(ast[1][1], (self.compile_set_literal(l) for l in ast[2][1])) }
            parallel_iterator_names = ast[1][1]

        return local_iterators, parallel_iterator_names


    # whereClause
    # ('Where', iteratorList)
    #
    def compile_whereClause(self, ast, iterators):
        local_iterators = {}
        parallel_iterator_names = []
        if ast[0] == 'Where':
            iterator_list = ast[1][1]

            for iter in iterator_list:
                ret = self.compile_iterator(iter)
                local_iterators.update(ret[0])
                parallel_iterator_names.extend(ret[1])

        # WhereIdList
        else:
            try:
                for iter_name in ast[1]:
                    local_iterators.update({iter_name: iterators[iter_name]})
            except KeyError as e:
                self.error("Undefined iterator `%s` is used in expression." % e.args)

        return local_iterators, set(parallel_iterator_names)


    # ifClause
    # ('If', iteratorList)
    #
    def compile_ifClause(self, ast, iterator_dicts):
        if_clauses = self.internal_outputter.output_qualified(ast, iterator_dicts)

        return (eval(clause, globals(), self.heap) for clause in if_clauses)


    # Compile iterator dicts to use on expression templates
    #
    def compile_iterator_dicts(self, iterators, iterator_names, parallel_iterator_names):
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
            other_iterators = ( iterators[k] for k in iterator_names.difference(parallel_iterator_names) )
        except KeyError as e:
            self.error("Undefined iterator `%s` is used in expression." % e.args)

        # Finally, take the cartesian product of all iterators
        if len(parallel_iterator_names) == 0:
            return (merge_dicts(dicts) for dicts in itertools.product(*other_iterators))
        else:
            return (merge_dicts(dicts) for dicts in itertools.product(parallel_iterators, *other_iterators))


    # Qualified Expressions
    # ('Qualified', expr, ifClause, whereClause)
    #
    # Compile iterators defined by the implicit iterators
    # present in the expression, and in the qualified expression
    # 'where' and 'if' clauses
    # NB: can take into account additional implicit iterators,
    # passed in the additional_iterator_names argument
    def compile_qualified(self, qualified_expr, iterators, iterator_names):

        # Compile whereClause to add explicit iterators, if any
        if not qualified_expr[3] is None:
            local_iterators, parallel_iterator_names = self.compile_whereClause(qualified_expr[3], iterators)
            iterators.update( local_iterators )
        else:
            parallel_iterator_names = set()

        # Compile expression
        # First, we need to build the dicts of iterators
        iterator_dicts = self.compile_iterator_dicts(iterators, iterator_names, parallel_iterator_names)

        # Compile ifClause, if any
        if not qualified_expr[2] is None:
            # Need to persist iterator_dicts
            iterator_dicts = list(iterator_dicts)
            if_filter = self.compile_ifClause(qualified_expr[2], iterator_dicts)
        else:
            if_filter = []

        # Apply if_filter to iterator_dicts
        iterator_dicts = [i for i, cond in itertools.izip_longest(iterator_dicts, if_filter, fillvalue = True) if cond]

        logger.log("Final iterators", iterator_dicts)

        return (qualified_expr[1], iterator_dicts, iterators)


    # Equation definition
    # ('EquationDef', option, expr, qualifiedExpr)
    #
    def compile_equation(self, ast):
        # Find iterators used in this qualified expression
        iterator_names = set(extract_iterators(ast[2])).union(extract_iterators(ast[3][1]))

        _, iterator_dicts, all_iterators = self.compile_qualified(ast[3], self.iterators.copy(), iterator_names)

        # Compile function calls
        lhs = ast[2] #, self.iterators.copy(), lhs_iterator_names)
        rhs = self.ast_functions(ast[3][1], all_iterators.copy())

        return (lhs, rhs, iterator_dicts)


    def compile_local_definition(self, ast):
        try:
            self.heap[ast[1]] = self.compile_set_literal(ast[2])
        # If we're assigning an integer directly
        except TypeError:
            self.heap[ast[1]] = ast[2]

    def compile(self, program):
        self.heap = {'V_01': 15, 'V_02': 0, 'V_03': 45, 'dV': 45}
        self.iterators = {'s': self.build_iterator('s', zip(['01', '02', '99'], range(1,4)))}
        self.lines = program.split('\n')
        self.current_line = 0

        self.internal_outputter = Outputter()

        # Parse the program
        ast = plyyacc.parser.parse(program)

        # Check for errors
        if len(plyyacc.errors) == 0:
            logger.log(ast, "\n")

            try:
                # Go through each statement
                for a in ast[1]:
                    s = a[1]
                    self.current_line = a[2]

                    if s[0] == 'EquationDef':
                        logger.log(self.internal_outputter.output_equation(*self.compile_equation(s)))

                    elif s[0] == 'LocalDef':
                        self.compile_local_definition(s)

                logger.log(self.heap)
                logger.log(self.iterators)
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
    compiler.compile("V[c] = sum(X[c, s] on s) where c in {01, 02}\n")
    # compiler.compile("""V[c] = x[c] + v[$c] where c in {01, 02} \ {01}
    # test[s] = 42
    # %sectors := {01, 02, 03} \ {02}
    # %year := 2006
    # X[s] = 12 if V[s] <> 0 where s in {01, 02, 03}
    # test = (X|O|[s] + v[$s]) / A|O|[s] where (O, V) in ({D, M}, {X, IA}), s in {01, 02, 03, 05}\n
    # #test = (X|O|[s] + v[$s]) / A|O|[s, s] + B[s] * (C[$s] / D[s]) where (O, V) in ({'D', 'M'}, {'X', 'IA'}), s in {'01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16'}\n""")

if __name__ == "__main__":
    if len(sys.argv) == 1:
        test()
    else:
        import timeit
        logger.enabled = False
        print(timeit.timeit('test()', setup="from __main__ import test", number=3000)/3000)

    # print plyyacc.parser.parse("""test = X|O|[1, 2]{t-1} if test > 2 where i in %c
    #                       %test := {"15", "05"}
    #                       functionTest = function()
    #                       functionTest2 = function(hello[c] where (c, s) in ({"01"}, {"05"}), world)
    #                       """)
