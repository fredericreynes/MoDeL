type operator =
  | Plus
  | Minus
  | Times
  | Div

type expr =
  | Number of int
  | UnOp of operator * expr
  | BinOp of operator * expr * expr

type line =
  | Equation of expr * expr
  | Assignment of expr * expr

val string_of_ast: expr -> string
