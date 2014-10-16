%{
open Ast
%}

%token <int> INT
%token PLUS MINUS TIMES DIV
%token LPAREN RPAREN
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
  | LPAREN e = expr RPAREN      { e }
  | e = expr PLUS f = expr      { BinOp(Plus, e, f) }
  | e = expr MINUS f = expr     { BinOp(Minus, e, f) }
  | e = expr TIMES f = expr     { BinOp(Times, e, f) }
  | e = expr DIV f = expr       { BinOp(Div, e, f) }
  | MINUS e = expr %prec UMINUS { UnOp(Minus, e) }
;
assignment:
  rhs = expr ASSIGN lhs = expr  { Assignment(rhs, lhs) }
;
equation:
  rhs = expr EQUAL lhs = expr   { Equation(rhs, lhs) }
;
