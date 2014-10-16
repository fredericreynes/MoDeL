type id_part =
  | Id of string
  | Placeholder of string

type operator =
  | Plus
  | Minus
  | Times
  | Div

type expr =
  | Number of int
  | UnOp of operator * expr
  | BinOp of operator * expr * expr
  | Function of string * expr list
  | Variable of id_part list * expr list * expr option

type line =
  | Equation of expr * expr
  | Assignment of expr * expr

val string_of_ast: expr -> string
