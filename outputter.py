import plylex
import re

# Test if a string is an id
id_pattern = re.compile('^' + plylex.id + '$')

def is_id(str):
    return bool(id_pattern.search(str))

class Outputter:

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
        try:
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

            elif ast[0] == 'CompiledFunctionCall':
                print 'Output function call', ast[2]
                test = list(ast[2])
                print "tet"
                print 'Output function call', test
                return getattr(self, ast[1])(ast[2])

        # Special case for terminals (ints, floats, etc.)
        except TypeError:
            return str(ast)

    # Qualified expression
    #
    # This function is used when a qualified expression stands alone,
    # in the parameters of a function
    def output_qualified(self, ast, iterator_dicts):
        # Get the compiled output version of this expression
        output = ''.join(self.output_expr(ast[1]))

        # This output is in turn just a template to be fed to the iterators
        return [output % iter_dict for iter_dict in iterator_dicts]

    # Equation
    #
    def output_equation(self, lhs, rhs, iterator_dicts):
        print "Output_equation", rhs
        # Get the compiled output version for both sides of the equation
        output = ''.join(self.output_expr(lhs)) + ' = ' + ''.join(self.output_expr(rhs))

        return [output % iter_dict for iter_dict in iterator_dicts]

    #
    # Functions
    #

    def sum(self, args):
        return '(' + ' + '.join(self.output_qualified(a) for a in args) + ')'
