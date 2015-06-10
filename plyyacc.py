import plylex
import ply.yacc as yacc

# Get the token map
tokens = plylex.tokens

precedence = (
               ('left', 'PLUS','MINUS'),
               ('left', 'TIMES','DIVIDE'),
               # ('left', 'POWER'),
               # ('right','UMINUS')
)

# Variables

def p_placeholder(p):
    '''placeholder: PIPE ID PIPE'''
    p[0] = ('Placeholder', p[2], p.lineno(2))

def p_variable_id(p):
    '''variable : ID'''
    p[0] = ('VarID', p[1], p.lineno(1))

def p_variable_id_placeholder(p):
    '''variable : '''

# Expressions

def p_expression_number(p):
    '''expr : INTEGER
            | FLOAT'''
    p[0] = ('ExprNumber', p[1], p.lineno(1))

def p_expression_localid(p):
    '''expr : LOCALID'''
    p[0] = ('ExprLocalID', p[1], p.lineno(1))

def p_expression_binary(p):
    '''expr : expr PLUS expr
            | expr MINUS expr
            | expr TIMES expr
            | expr DIVIDE expr'''
    p[0] = ('ExprBinary', p[2], p[1], p[3], p.lineno(2))

def p_expression_group(p):
    '''expr : LPAREN expr RPAREN'''
    p[0] = ('ExprGroup', p[2], p.lineno(2))

parser = yacc.yacc()

if __name__ == "__main__":
    print parser.parse("52 * 5 + 4")
