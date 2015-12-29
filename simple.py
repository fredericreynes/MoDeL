from simpleparse.common import numbers
from simpleparse.parser import Parser
from simpleparse.dispatchprocessor import *

declaration = '''
main            := expr

# Keywords
<keywords>      := 'where'/'on'/'in'

# Identifiers
id              := [_a-zA-Z], [_a-zA-Z]*
placeholder     := '|', id, '|'
identifier      := (id/placeholder)+

# Local variables
local           := '%', [_a-zA-Z], [_a-zA-Z]*

# Series
index           := '[', (expr, (ts?, ',', ts?)?)+, ']'!"Missing closing bracket in index"
time            := '{', int, '}'!"Missing closing brace in time index"
series          := identifier, index?, time?

# Variable
variable        := series

# Functions
function        := id, '(', (qualified, (ts?, ',', ts?)?)+,')'

# Expressions
expr            := inner_expr / paren_expr
>inner_expr<    := term, ((ts?, op, ts?, term)+)?
>term<          := ( (function / variable / paren_expr), ts, ?keywords ) /
                   ( (function / variable / paren_expr), ?-(ts, variable / paren_expr)!"Missing operator between two operands" )
paren_expr      := '(', ts?, inner_expr, ts?, ')'!"Missing closing parenthesis"
op              := [-+/*<>]

# Qualified expressions
whereClause     := 'where'/'on', ts, id, (ts, 'in', ts, local)?
ifClause        := 'if', ts, expr
qualified       := expr, whereClause?, ifClause?

# Equation
equation        := expr, '=', qualified

# Series definition
definition      := expr, ':=', qualified

# Whitespace
<ts>            := [ \011]+
<nl>            := '\n'

# Comments
comment         := '#',-'\n'*,'\n'
'''

class CustomProcessor(DispatchProcessor):
    def identifier(self, (tag,start,stop,subtags), buffer):
        return self.getString((tag,start,stop,subtags), buffer)

parser = Parser(declaration, "main")
success, ast, nextchar = parser.parse("test|g|[c, d]{1} > ( c)\n")
success, ast, nextchar = parser.parse("test(c on f)\n")

import pprint
pprint.pprint(ast)


backup = '''
#expr           := (simple_expr, no_binop) / binop_expr, ts?
#binop_expr     := simple_expr, binop_tail
#binop_tail     := ts, binop, ts, expr
#>simple_expr<  := paren_expr / unop_expr / variable
#>no_binop<     := ?-binop
#paren_expr     := '(', expr, ')'
#unop_expr      := unop, expr
#unop           := [+-]
#binop          := [+/*-]
'''
