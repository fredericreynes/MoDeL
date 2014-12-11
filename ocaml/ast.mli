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

type lst_expr =
  | Lst of IndexedList.t
  | BinOp of operator * lst_expr * lst_expr
  | Local of string

type iterator = Iterator of string * lst_expr option

type full_expr = FullExpr of expr * iterator option

type statement =
  | Equation of expr * expr
  | AssignExpr of expr * expr
  | AssignLst of expr * lst_expr

val apply_assignments : statement list -> unit

val string_of_expr : expr -> string

val compile_lst_expr : lst_expr -> IndexedList.t

val heap : (string, IndexedList.t) Hashtbl.t
