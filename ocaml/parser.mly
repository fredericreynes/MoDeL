/* File parser.mly */
%{
open Ast
%}
%token <int> INT
%token PLUS MINUS TIMES DIV
%token LPAREN RPAREN
%token EOL EOF
%left PLUS MINUS        /* lowest precedence */
%left TIMES DIV         /* medium precedence */
%nonassoc UMINUS        /* highest precedence */
%start main             /* the entry point */
%type <Ast.ast> main
%%
main:
  e = expr EOL                  { e }
;
number:
  i = INT                       { i }
;
expr:
    n = number                  { Number n }
  | LPAREN e = expr RPAREN      { e }
  | e = expr PLUS f = expr      { BinOp(Plus, e, f) }
  | e = expr MINUS f = expr     { BinOp(Minus, e, f) }
  | e = expr TIMES f = expr     { BinOp(Times, e, f) }
  | e = expr DIV f = expr       { BinOp(Div, e, f) }
  | MINUS e = expr %prec UMINUS { UnOp(Minus, e) }
;
