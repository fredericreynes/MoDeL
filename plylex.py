import ply.lex as lex
from ply.lex import TOKEN

# Reserved words
reserved = (
    'WHERE', 'ON', 'IF', 'IN',
    )


tokens = reserved + (
    # Literals (identifier, local identifier, integer constant, float constant, string constant)
    'ID', 'COUNTERID', 'PLACEHOLDER', 'LOCALID', 'INTEGER', 'FLOAT', 'STRING',

    # Operators (+, -, *, /, &, ~, ^, !, <, <=, >, >=, ==, !=)
    'PLUS', 'MINUS', 'TIMES', 'DIVIDE',
    'AND', 'NOT', 'XOR', 'LNOT',
    'LT', 'GT', 'LE', 'GE', 'EQ', 'NE',

    # Assignment (=, :=)
    'EQUALS', 'SERIESEQUALS',

    # Delimeters ( ) [ ] { } , . | ;
    'LPAREN', 'RPAREN',
    'LBRACKET', 'RBRACKET',
    'LBRACE', 'RBRACE',
    'COMMA', 'PERIOD',
    'PIPE', 'BACKLASH', 'SEMI',
    'NEWLINE', 'COMMENT',

    # Ellipsis (...)
    'ELLIPSIS',
    )

# Completely ignored characters
t_ignore           = ' \t\x0c'


# Newlines
def t_NEWLINE(t):
    r'\n+'
    t.lexer.lineno += t.value.count("\n")
    return t

# Operators
t_PLUS             = r'\+'
t_MINUS            = r'-'
t_TIMES            = r'\*'
t_DIVIDE           = r'/'
t_AND              = r'&'
t_NOT              = r'~'
t_XOR              = r'\^'
t_LNOT             = r'!'
t_LT               = r'<'
t_GT               = r'>'
t_LE               = r'<='
t_GE               = r'>='
t_EQ               = r'=='
t_NE               = r'!='

# Assignment operators

t_EQUALS           = r'='
t_SERIESEQUALS     = r':='

# Delimeters
t_LPAREN           = r'\('
t_RPAREN           = r'\)'
t_LBRACKET         = r'\['
t_RBRACKET         = r'\]'
t_LBRACE           = r'\{'
t_RBRACE           = r'\}'
t_COMMA            = r','
t_PERIOD           = r'\.'
t_PIPE             = r'\|'
t_BACKLASH         = r'\\'
t_SEMI             = r';'


# Identifiers and reserved words

reserved_map = { }
for r in reserved:
    reserved_map[r.lower()] = r

# Identifier
id                = r'[A-Za-z_][\w_]*'

@TOKEN(id)
def t_ID(t):
    t.type = reserved_map.get(t.value,"ID")
    return t

# Counter id
t_COUNTERID        = r'\$[A-Za-z]\w*'

# Placeholder
placeholder        = r'\|(' + id + ')\|'

@TOKEN(placeholder)
def t_PLACEHOLDER(t):
    t.value = t.lexer.lexmatch.group(3)
    return t

# Local identifier
t_LOCALID          = r'%[_a-zA-Z0-9]+'

# Integer literal
def t_INTEGER(t):
    r'[0-9]+'
    # Hackish: also preserve the original int as a string
    # for use in set definitions
    t.value = (int(t.value), t.value)
    return t

# Float literal
def t_FLOAT(t):
    r'( (\d+)(\.\d+)(e(\+|-)?(\d+))? | (\d+)e(\+|-)?(\d+) )'
    t.value = float(t.value)
    return t

# String literal
def t_STRING(t):
    r'\"([^\\\n]|(\\.))*?\" | \'([^\\\n]|(\\.))*?\''
    #r"'(''|[^'])*'"
    t.value = t.value[1:-1]
    return t

# Comments
def t_COMMENT(t):
    r'\#.*'
    #t.lexer.lineno += 1
    return t

def t_error(t):
    print("Illegal character %s" % repr(t.value[0]))
    t.lexer.skip(1)

lexer = lex.lex()
if __name__ == "__main__":
    lex.runmain(lexer)
