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
    '''statement : equation NEWLINE
                 | series NEWLINE'''
    p[0] = ('Statement', p[1], p.lineno(2))


# Variable id

def p_placeholder(p):
    '''placeholder : PLACEHOLDER'''
    p[0] = ('Placeholder', p[1])

def p_variable_id_simple(p):
    '''variableId : ID'''
    p[0] = ('VarId', (p[1], ))

def p_variable_id_placeholder(p):
    '''variableId : placeholder'''
    p[0] = ('VarId', (p[1], ))

def p_variable_id_recursive(p):
    '''variableId : variableId placeholder
                    | variableId ID'''
    p[0] = ('VarId', p[1][1] + (p[2], ))


# Variable name

def p_index(p):
    '''index : LBRACKET exprList RBRACKET'''
    p[0] = ('Index', p[2])

def p_index_single(p):
    '''index : LBRACKET expr RBRACKET'''
    p[0] = ('Index', (p[2], ))

def p_time(p):
    '''time : LBRACE expr RBRACE'''
    p[0] = ('Time', p[2])

def p_variable_name(p):
    '''variableName : variableId'''
    p[0] = ('VarName', (p[1], ))

def p_variable_name_index(p):
    '''variableName : variableId index'''
    p[0] = ('VarName', (p[1], p[2]))

def p_variable_name_time(p):
    '''variableName : variableId time'''
    p[0] = ('VarName', (p[1], p[2]))

def p_variable_name_index_time(p):
    '''variableName : variableId index time'''
    p[0] = ('VarName', (p[1], p[2], p[3]))


# Definitions

def p_where_clause(p):
    '''whereClause : WHERE ID IN LOCALID
                   | ON ID IN LOCALID'''
    p[0] = ('Where', (p[2],), (p[4],))

def p_if_clause(p):
    '''ifClause : IF expr'''
    p[0] = ('If', p[2])

def p_qualified_expression(p):
    '''qualifiedExpr : expr'''
    p[0] = ('Qualified', p[1], )

def p_qualified_expression_where(p):
    '''qualifiedExpr : expr whereClause'''
    p[0] = ('Qualified', p[1], p[2])

def p_qualified_expression_if(p):
    '''qualifiedExpr : expr ifClause'''
    p[0] = ('Qualified', p[1], p[2])

def p_qualified_expression_if_where(p):
    '''qualifiedExpr : expr ifClause whereClause'''
    p[0] = ('Qualified', p[1], p[2], p[3])

def p_equation(p):
    '''equation : expr EQUALS qualifiedExpr'''
    p[0] = ('Equation', None, p[1], p[3])

def p_series(p):
    '''series : expr SERIESEQUALS qualifiedExpr'''
    p[0] = ('Series', None, p[1], p[3])

# Expressions

def p_expression_terminal(p):
    '''expr : INTEGER
            | FLOAT
            | LOCALID
            | variableName'''
    p[0] = p[1]

def p_expression_binary(p):
    '''expr : expr PLUS expr
            | expr MINUS expr
            | expr TIMES expr
            | expr DIVIDE expr
            | expr LT expr
            | expr GT expr
            | expr LE expr
            | expr GE expr'''
    p[0] = ('ExprBinary', p[2], p[1], p[3])

def p_expression_group(p):
    '''expr : LPAREN expr RPAREN'''
    p[0] = ('ExprGroup', p[2], )

def p_expression_list(p):
    '''exprList : expr'''
    p[0] = (p[1], )

def p_expression_list_recursive(p):
    '''exprList : exprList COMMA expr'''
    p[0] =  p[1] + (p[3], )

parser = yacc.yacc()

if __name__ == "__main__":
    print parser.parse("t = X|O|[1, 2]{t-1} if pouet > 2 where i in %c\n")
