type operator =
  Plus
| Minus
| Times
| Div

type ast =
  Number of int
| UnOp of operator * ast
| BinOp of operator * ast * ast

val string_of_ast: ast -> string
