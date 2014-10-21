type id_part =
  | Id of string
  | Placeholder of string

type operator =
  | Plus
  | Minus
  | Times
  | Div

type str_or_int =
  | Str of string
  | Intg of int

type expr =
  | None
  | Number of int
  | UnOp of operator * expr
  | BinOp of operator * expr * expr
  | Function of string * expr list
  | Variable of id_part list * expr list * expr option
  | Local of string

type lst = Lst of string list * string list option

type statement =
  | Equation of expr * expr
  | AssignExpr of expr * expr
  | AssignLst of expr * lst

val apply_assignments : statement list -> unit

val heap : (string, lst) Hashtbl.t
