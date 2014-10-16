%{
open Ast
%}

%token <int> INT
%token <string> ID
%token PLUS MINUS TIMES DIV
%token LPAREN RPAREN
%token COMMA
%token EOL EOF
%token EQUAL ASSIGN

%left PLUS MINUS        /* lowest precedence */
%left TIMES DIV         /* medium precedence */
%nonassoc UMINUS        /* highest precedence */

%start main             /* the entry point */
%type <Ast.line list> main

%%
main:
    l = line EOF                { [l] }
  | l = line m = main           { l :: m }
;
line:
    l = assignment EOL          { l }
  | l = equation EOL            { l }
;
number:
  i = INT                       { i }
;
expr:
    n = number                  { Number n }
  | MINUS e = expr %prec UMINUS { UnOp(Minus, e) }
  | e = expr PLUS f = expr      { BinOp(Plus, e, f) }
  | e = expr MINUS f = expr     { BinOp(Minus, e, f) }
  | e = expr TIMES f = expr     { BinOp(Times, e, f) }
  | e = expr DIV f = expr       { BinOp(Div, e, f) }
  | LPAREN e = expr RPAREN      { e }
  | f = func                    { f }
;
assignment:
  rhs = expr ASSIGN lhs = expr  { Assignment(rhs, lhs) }
;
equation:
  rhs = expr EQUAL lhs = expr   { Equation(rhs, lhs) }
;
func:
  id = ID params = delimited(LPAREN, separated_nonempty_list(COMMA, expr), RPAREN)       { Function(id, params) }
;
