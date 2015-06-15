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

# Entry point

def p_program(p):
    '''program : statement'''
    p[0] = ('Program', (p[1], ))

def p_program_recursive(p):
    '''program : program statement'''
    p[0] = ('Program', p[1][1] + (p[2], ))

# Statements

def p_statement(p):
    '''statement : variableName NEWLINE
                 | expr NEWLINE'''
    p[0] = ('Statement', p[1], p.lineno(2))

# Variables

def p_placeholder(p):
    '''placeholder : PLACEHOLDER'''
    p[0] = ('Placeholder', p[1])

def p_variable_name_id(p):
    '''variableName : ID'''
    p[0] = ('VarName', (p[1], ))

def p_variable_name_placeholder(p):
    '''variableName : placeholder'''
    p[0] = ('VarName', (p[1], ))

def p_variable_name_recursive(p):
    '''variableName : variableName placeholder
                    | variableName ID'''
    print type(p[2][1]), p[2][1]
    p[0] = ('VarName', p[1][1] + (p[2], ))


# Expressions

def p_expression_number(p):
    '''expr : INTEGER
            | FLOAT'''
    p[0] = ('ExprNumber', p[1])

def p_expression_localid(p):
    '''expr : LOCALID'''
    p[0] = ('ExprLocalID', p[1])

def p_expression_binary(p):
    '''expr : expr PLUS expr
            | expr MINUS expr
            | expr TIMES expr
            | expr DIVIDE expr'''
    p[0] = ('ExprBinary', p[2], p[1], p[3])

def p_expression_group(p):
    '''expr : LPAREN expr RPAREN'''
    p[0] = ('ExprGroup', p[2])

parser = yacc.yacc()

if __name__ == "__main__":
    print parser.parse("X|O||F|\nX\n|P|\n")
