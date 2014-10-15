/* File parser.mly */
%{
open Ast
%}
%token <int> INT
%token PLUS MINUS TIMES DIV
%token LPAREN RPAREN
%token EOL
%left PLUS MINUS        /* lowest precedence */
%left TIMES DIV         /* medium precedence */
%nonassoc UMINUS        /* highest precedence */
%start main             /* the entry point */
%type <Ast.ast> main
%%
main:
    expr EOL                { $1 }
;
number:
  INT                       { $1 }
expr:
    number                  { Number $1 }
  | LPAREN expr RPAREN      { $2 }
  | expr PLUS expr          { BinOp(Plus, $1, $3) }
  | expr MINUS expr         { BinOp(Minus, $1, $3) }
  | expr TIMES expr         { BinOp(Times, $1, $3) }
  | expr DIV expr           { BinOp(Div, $1, $3) }
  | MINUS expr %prec UMINUS { UnOp(Minus, $2) }
;
