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


# Statement

def p_statement(p):
    '''statement : equationDef NEWLINE
                 | seriesDef NEWLINE
                 | localDef NEWLINE
                 | comment NEWLINE'''
    p[0] = ('Statement', p[1], p.lineno(2))

# Comment

def p_comment(p):
    '''comment : COMMENT'''
    p[0] = ('Comment', p[1])

# Variable id

def p_placeholder(p):
    '''placeholder : PLACEHOLDER'''
    p[0] = ('Placeholder', p[1][1:-1])

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

# def p_index_single(p):
#     '''index : LBRACKET expr RBRACKET'''
#     p[0] = ('Index', (p[2], ))

def p_time(p):
    '''time : LBRACE expr RBRACE'''
    p[0] = ('Time', p[2])

def p_variable_name(p):
    '''variableName : variableId'''
    p[0] = ('VarName', p[1], None, None)

def p_variable_name_index(p):
    '''variableName : variableId index'''
    p[0] = ('VarName', p[1], p[2], None)

def p_variable_name_time(p):
    '''variableName : variableId time'''
    p[0] = ('VarName', p[1], None, p[2])

def p_variable_name_index_time(p):
    '''variableName : variableId index time'''
    p[0] = ('VarName', p[1], p[2], p[3])


# List literals

def p_string_list(p):
    '''stringList : STRING'''
    p[0] = ('StringList', (p[1], ))

def p_string_list_recursive(p):
    '''stringList : stringList COMMA STRING'''
    p[0] =  ('StringList', p[1][1] + (p[3], ))

def p_list_literal(p):
    '''listLiteral : LBRACE stringList RBRACE'''
    p[0] = ('ListLiteral', p[2][1])


# Expressions

def p_expression_terminal(p):
    '''expr : INTEGER
            | FLOAT
            | LOCALID
            | variableName
            | functionCall'''
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
    p[0] = ('ExprGroup', p[2])

def p_expression_list(p):
    '''exprList : expr'''
    p[0] = ('ExprList', (p[1], ))

def p_expression_list_recursive(p):
    '''exprList : exprList COMMA expr'''
    p[0] =  ('ExprList', p[1][1] + (p[3], ))


# Lists of LocalID, ID, and Lists

def p_localid_list(p):
    '''localidList : LOCALID'''
    p[0] = ('LocalIDList', (p[1], ))

def p_localid_list_recursive(p):
    '''localidList : localidList COMMA LOCALID'''
    p[0] =  ('LocalIDList', p[1][1] + (p[3], ))

def p_localid_group(p):
    '''localidGroup : LPAREN localidList RPAREN'''
    p[0] = ('LocalIDGroup', p[2][1])

def p_id_list(p):
    '''idList : ID'''
    p[0] = ('IDList', (p[1], ))

def p_id_list_recursive(p):
    '''idList : idList COMMA ID'''
    p[0] =  ('IDList', p[1][1] + (p[3], ))

def p_id_group(p):
    '''idGroup : LPAREN idList RPAREN'''
    p[0] = ('IDGroup', p[2][1])

def p_list_list(p):
    '''listList : listLiteral'''
    p[0] = ('ListList', (p[1], ))

def p_list_list_recursive(p):
    '''listList : listList COMMA listLiteral'''
    p[0] =  ('ListList', p[1][1] + (p[3], ))

def p_list_group(p):
    '''listGroup : LPAREN listList RPAREN'''
    p[0] = ('ListGroup', p[2][1])


# Iterators

def p_iterator_list_literal(p):
    '''iterator : ID IN listLiteral'''
    p[0] = ('IteratorListLiteral', p[1], p[3])

def p_iterator_local(p):
    '''iterator : ID IN LOCALID'''
    p[0] = ('IteratorLocal', p[1], p[3])

def p_iterator_parallel_list(p):
    '''iterator : idGroup IN listGroup'''
    if len(p[1][1]) == len(p[3][1]):
        #add_error("Syntax error in parallel list iterator. %i variables for %i lists." % (len(p[1][1]), len(p[3][1])), p.lineno(2))
        p[0] = ('IteratorParallelList', p[1], p[3])
    # Different number of ids and lists
    else:
        add_error("Syntax error in parallel list iterator. %i variables for %i lists." % (len(p[1][1]), len(p[3][1])), p.lineno(2))

def p_iterator_parallel_local(p):
    '''iterator : idGroup IN localidGroup'''
    if len(p[1][1]) == len(p[3][1]):
        p[0] = ('IteratorParallelLocal', p[1], p[3])
    # Different number of variables and local ids
    else:
        add_error("Syntax error in parallel list iterator. %i variables for %i lists." % (len(p[1][1]), len(p[3][1])), p.lineno(2))

def p_iterator_parallel_list_error(p):
    '''iterator : ID IN listGroup'''
    add_error("Syntax error in parallel list iterator. 1 variable for %i lists." % len(p[3][1]), p.lineno(2))

def p_iterator_parallel_local_error(p):
    '''iterator : ID IN localidGroup'''
    add_error("Syntax error in parallel list iterator. 1 variable for %i lists." % len(p[3][1]), p.lineno(2))

def p_iterator_parallel_list_error(p):
    '''iterator : idGroup IN listLiteral'''
    add_error("Syntax error in parallel list iterator. %i variables for 1 list." % len(p[1][1]), p.lineno(2))

def p_iterator_parallel_local_error(p):
    '''iterator : idGroup IN LOCALID'''
    add_error("Syntax error in parallel list iterator. %i variables for 1 list." % len(p[1][1]), p.lineno(2))


# Qualified expressions

def p_where_clause(p):
    '''whereClause : WHERE iterator
                   | ON iterator'''
    p[0] = ('Where', p[2])

def p_if_clause(p):
    '''ifClause : IF expr'''
    p[0] = ('If', p[2])

def p_qualified_expression(p):
    '''qualifiedExpr : expr'''
    p[0] = ('Qualified', p[1], None, None)

def p_qualified_expression_where(p):
    '''qualifiedExpr : expr whereClause'''
    p[0] = ('Qualified', p[1], None, p[2])

def p_qualified_expression_if(p):
    '''qualifiedExpr : expr ifClause'''
    p[0] = ('Qualified', p[1], p[2], None)

def p_qualified_expression_if_where(p):
    '''qualifiedExpr : expr ifClause whereClause'''
    p[0] = ('Qualified', p[1], p[2], p[3])

def p_qualified_expression_list(p):
    '''qualifiedExprList : qualifiedExpr'''
    p[0] = ('QualifiedExprList', (p[1], ))

def p_qualified_expression_list_recursive(p):
    '''qualifiedExprList : qualifiedExprList COMMA qualifiedExpr'''
    p[0] =  ('QualifiedExprList', p[1][1] + (p[3], ))


# Function

def p_function(p):
    '''functionCall : ID LPAREN RPAREN'''
    p[0] = ('FunctionCallNoArgs', p[1])

def p_function_with_arguments(p):
    '''functionCall : ID LPAREN qualifiedExprList RPAREN'''
    p[0] = ('FunctionCallArgs', p[1], p[3])


# Definitions

def p_equation_definition(p):
    '''equationDef : expr EQUALS qualifiedExpr'''
    p[0] = ('EquationDef', None, p[1], p[3])

def p_series_definition(p):
    '''seriesDef : expr SERIESEQUALS qualifiedExpr'''
    p[0] = ('SeriesDef', None, p[1], p[3])

def p_local_definition(p):
    '''localDef : LOCALID SERIESEQUALS listLiteral'''
    p[0] = ('LocalDef', p[1], p[3])


# Error
def add_error(msg, line_nb):
    errors.append((msg, line_nb))


parser = yacc.yacc()

errors = []

if __name__ == "__main__":
    print parser.parse("""pouet[c] = 15 where i in {"15", "10"}

    t = X|O|[s, 2]{t-1} if test > 2 where i in %c
    #                      %test := {"15", "05"}
    #                      functionTest = function()
    #                      functionTest2 = function(hello[c] where (c, s) in ({"01"}, {"05"}), world)
                          """)
