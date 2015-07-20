from functools import wraps
import itertools
import plylex
import plyyacc
import re

import sys
import logger

def build_variable(name):
    ('VarName', ('VarId', (name,)), None, None)

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
        if ast[0] == 'VarName':
            return itertools.chain(wrapped_func(ast[1]), wrapped_func(ast[2]), wrapped_func(ast[3]))
        elif ast[0] == 'VarId':
            return itertools.chain.from_iterable(wrapped_func(a) for a in ast[1])
        elif ast[0] == 'Placeholder':
            return wrapped_func(ast[1])
        elif ast[0] == 'Index':
            return wrapped_func(ast[1])
        elif ast[0] == 'ExprList':
            return itertools.chain.from_iterable(wrapped_func(a) for a in ast[1])
        elif ast[0] == 'ExprBinary':
            return itertools.chain(wrapped_func(ast[2]), wrapped_func(ast[3]))
        elif ast[0] == 'ExprGroup':
            return wrapped_func(ast[1])
        elif ast[0] == 'FunctionCallArgs':
            return wrapped_func(ast[2])
        elif ast[0] == 'QualifiedExprList':
            return itertools.chain.from_iterable(wrapped_func(a) for a in ast[1])
        elif ast[0] == 'Qualified':
            return itertools.chain(wrapped_func(ast[1]), wrapped_func(ast[2]), wrapped_func(ast[3]))
        elif ast[0] == 'EquationDef':
            return itertools.chain(wrapped_func(ast[2]), wrapped_func(ast[3]))
        else:
            return iter([])

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

# Test if a string is an id
id_pattern = re.compile('^' + plylex.id + '$')

def is_id(str):
    return bool(id_pattern.search(str))

class CompilerError(Exception):
    pass

class Compiler:

    #
    # External interface
    #
    # This is the interface that has to be modified
    # for each implementation of the Compiler class
    #

    # ExprBinary
    #
    def output_expr_binary(self, op, output_lhs, output_rhs):
        return output_lhs + ' ' + op + ' ' + output_rhs

    # ExprGroup
    #
    def output_expr_group(self, output_expr):
        return '(' + output_expr + ')'

    # Index (single)
    #
    def output_index(self, output_expr):
        # If the index is a single varid, then it is an iterator
        if is_id(output_expr):
            return '%(' + output_expr + ')s'
        # Else it's an expression containing a counter of the form $i,
        # which should have been already compiled correctly
        else:
            return output_expr

    # Indices
    #
    def output_indices(self, output_indexList):
        return '_'.join(output_indexList)

    # Time offset
    #
    def output_timeOffset(self, output_timeExpr):
        return '{' + output_timeExpr + '}'

    # VarName
    #
    def output_varname(self, output_variableId, output_indices, output_timeOffset):
        return output_variableId + ('_' if len(output_indices) > 0 else '') + output_indices + output_timeOffset

    # Placeholder
    #
    def output_placeholder(self, placeholder):
        return '%(' + placeholder + ')s'

    # CounterId
    #
    def output_counterid(self, counterid):
        return '%(' + counterid + ')s'

    # VarId part
    #
    def output_varid_part(self, part):
        # Placeholders must be further treated
        if part[0] == 'Placeholder':
            return self.output_placeholder(part[1])
        # Straight strings pass through directly
        else:
            return part

    # VarId
    #
    def output_varid(self, output_varId_parts):
        return ''.join(output_varId_parts)

    # Expression
    #
    def output_expr(self, ast):
        # ('ExprBinary', op, lhs, rhs)
        if ast[0] == 'ExprBinary':
            return self.output_expr_binary(ast[1], self.output_expr(ast[2]), self.output_expr(ast[3]))
        # ('ExprGroup', expr)
        elif ast[0] == 'ExprGroup':
            return self.output_expr_group(self.output_expr(ast[1]))
        # ('VarName', variableId, index, time)
        elif ast[0] == 'VarName':
            indices = ast[2][1][1] if ast[2] else []
            return self.output_varname(self.output_varid(self.output_varid_part(vid) for vid in ast[1][1]),
                                       self.output_indices(self.output_index(self.output_expr(i)) for i in indices),
                                       self.output_timeOffset(ast[3]) if ast[3] else '')
        # ('CounterId', counterId)
        elif ast[0] == 'CounterId':
            return self.output_counterid(ast[1])

    # Qualified expression
    #
    def output_qualified(self, ast, iterator_dicts):
        # Get the compiled output version of this expression
        output = ''.join(self.output_expr(ast))

        # This output is in turn just a template to be fed to the iterators
        return [output % iter_dict for iter_dict in iterator_dicts]



    #
    # Compiler internals
    #
    # This is common to all Compiler instances,
    # and doesn't need to be modified by the external interface
    #

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


    # From an iterator name `i` and its elements [i1, i2, ...], builds a list of dicts:
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

        return local_iterators, set(parallel_iterator_names)


    # Compile iterator dicts to use on expression templates
    #
    def compile_iterator_dicts(self, ast, iterators, parallel_iterator_names):
        # Find iterators used in this expression
        iterator_names = set(extract_iterators(ast))

        # Compile the iterators we need in this expression

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
            return [merge_dicts(dicts) for dicts in itertools.product(*other_iterators)]
        else:
            return [merge_dicts(dicts) for dicts in itertools.product(parallel_iterators, *other_iterators)]


    # Qualified Expressions
    # ('Qualified', expr, ifClause, whereClause)
    #
    def compile_qualified(self, ast, iterators):
        # Compile whereClause to add explicit iterators, if any
        if not ast[3] is None:
            local_iterators, parallel_iterator_names = self.compile_whereClause(ast[3])
            iterators.update( local_iterators )

        # Compile ifClause, if any

        # Compile expression

        # First, we need to build the dicts of iterators
        iterator_dicts = self.compile_iterator_dicts(ast[1], iterators, parallel_iterator_names)
        # We can then output the expression
        outputs= self.output_qualified(ast[1], iterator_dicts)

        logger.log("Final iterators", iterator_dicts)
        logger.log("Output", outputs)


    def compile(self, program):
        self.heap = {}
        self.iterators = {'test': ['01', '02', '99']}
        self.lines = program.split('\n')
        self.current_line = 0

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
    compiler.compile("""V = x[c] + v[$c] where c in {'01', '02'}
    test = X|O|[s] where (O, V) in ({'D', 'M'}, {'X', 'IA'}), s in {'14', '15', '16'}\n""")

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
