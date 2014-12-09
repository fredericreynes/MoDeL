type id_part =
  | Id of string
  | Placeholder of string

type str_or_int =
  | Str of string
  | Intg of int

type operator =
  | Plus
  | Minus
  | Times
  | Div

type expr =
  | None
  | Number of int
  | UnOp of operator * expr
  | BinOp of operator * expr * expr
  | Function of string * expr list
  | Variable of id_part list * expr list * expr option
  | Local of string

type lst = string list

type lst_expr =
  | Lst of lst
  | BinOp of operator * lst_expr * lst_expr
  | Local of string

type statement =
  | Equation of expr * expr
  | AssignExpr of expr * expr
  | AssignLst of expr * lst_expr

val apply_assignments : statement list -> unit

val string_of_expr : expr -> string

val compile_lst_expr : lst_expr -> lst

val set_of_lst : StringSet.elt list -> StringSet.t

val heap : (string, lst) Hashtbl.t
