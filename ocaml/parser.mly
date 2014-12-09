%{
open Ast
%}

%token <string> INT
%token <string> ID
%token <string> LOCAL
%token <string> STRING
%token PLUS MINUS TIMES DIV
%token EQUAL ASSIGN
%token LPAREN RPAREN
%token LBRACKET RBRACKET
%token LCURLY RCURLY
%token PIPE
%token BACKSLASH
%token COMMA
%token WS
%token EOL EOF

%left PLUS MINUS BACKSLASH        /* lowest precedence */
%left TIMES DIV         /* medium precedence */
%nonassoc UMINUS        /* highest precedence */

%start main             /* the entry point */
%type <Ast.statement list> main

%%
main:
                                    { [] }
  | s = statement EOF               { [s] }
  | s = statement EOL m = main      { s :: m }
;
statement:
    s = assign_expr                 { s }
  | s = assign_list                 { s }
  (* | rhs = expr ASSIGN lhs = lst   { AssignLst(rhs, lhs) } *)
  (* | rhs = expr EQUAL lhs = expr   { Equation(rhs, lhs) } *)
;
number:
  i = INT                       { i }
;
expr:
    n = number                  { Number (int_of_string n) }
  | MINUS e = expr %prec UMINUS { UnOp(Minus, e) }
  | e = expr PLUS f = expr      { BinOp(Plus, e, f) }
  | e = expr MINUS f = expr     { BinOp(Minus, e, f) }
  | e = expr TIMES f = expr     { BinOp(Times, e, f) }
  | e = expr DIV f = expr       { BinOp(Div, e, f) }
  | LPAREN e = expr RPAREN      { e }
  | f = func                    { f }
  | var = variable              { var }
  | local = LOCAL               { Local local }
;
id_part:
    id = ID                     { Id id }
  | PIPE id = ID PIPE           { Placeholder id }
;
variable:
  ident = nonempty_list(id_part)
  index = loption(delimited(LBRACKET, separated_nonempty_list(COMMA, expr), RBRACKET))
  time = option(delimited(LCURLY, expr, RCURLY))
  { Variable(ident, index, time) }
;
assign_expr:
    rhs = expr ASSIGN lhs = expr  { AssignExpr(rhs, lhs) }
;
assign_list:
    rhs = expr ASSIGN lhs = lst_expr  { AssignLst(rhs, lhs) }
;


str_or_int:
    str = STRING                { str }
  | int = INT                   { int }
;
lst:
   LCURLY
   l = separated_nonempty_list(COMMA, str_or_int)
   RCURLY
   { IndexedList.of_list l }
;
lst_expr:
    l = lst                                      { Lst l }
  | lel = lst_expr PLUS ler = lst_expr           { BinOp(Plus, lel, ler) }
  | lel = lst_expr BACKSLASH ler = lst_expr      { BinOp(Minus, lel, ler) }
  | LPAREN le = lst_expr RPAREN                  { le }
  | local = LOCAL                                { Local local }
;


func:
  id = ID params = delimited(LPAREN, separated_nonempty_list(COMMA, expr), RPAREN)       { Function(id, params) }
;
