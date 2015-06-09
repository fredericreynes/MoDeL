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

def p_expression_number(p):
    '''expr : INTEGER
            | FLOAT'''
    p[0] = ('Number', p[1])


parser = yacc.yacc()

if __name__ == "__main__":
    print parser.parse("5")
