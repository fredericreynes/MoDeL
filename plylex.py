import ply.lex as lex

# Reserved words
reserved = (
    'WHERE', 'ON', 'IF',
    )


tokens = reserved + (
    # Literals (identifier, local identifier, integer constant, float constant, string constant)
    'ID', 'LOCALID', 'INTEGER', 'FLOAT', 'STRING',

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
    'COMMA', 'PERIOD', 'PIPE', 'SEMI',

    # Ellipsis (...)
    'ELLIPSIS',
    )

# Completely ignored characters
t_ignore           = ' \t\x0c'


# Newlines
def t_NEWLINE(t):
    r'\n+'
    t.lexer.lineno += t.value.count("\n")

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
t_SEMI             = r';'


# Identifiers and reserved words

reserved_map = { }
for r in reserved:
    reserved_map[r.lower()] = r

# Identifier
t_ID               = r'[a-zA-Z]([_a-zA-Z0-9]+)?'

# Local identifier
t_LOCALID          = r'%[_a-zA-Z0-9]+'

# Integer literal
t_INTEGER           = r'[0-9]+'

# Float literal
t_FLOAT           = r'( (\d+)(\.\d+)(e(\+|-)?(\d+))? | (\d+)e(\+|-)?(\d+) )'

# String literal
t_STRING = r'\"([^\\\n]|(\\.))*?\"'

# Comments
def t_comment(t):
    r'^\#.*'
    t.lexer.lineno += 1

def t_error(t):
    print("Illegal character %s" % repr(t.value[0]))
    t.lexer.skip(1)

lexer = lex.lex()
if __name__ == "__main__":
    lex.runmain(lexer)
