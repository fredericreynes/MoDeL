module StringSet :
  sig
    type elt = String.t
    type t = Set.Make(String).t
    val empty : t
    val is_empty : t -> bool
    val mem : elt -> t -> bool
    val add : elt -> t -> t
    val singleton : elt -> t
    val remove : elt -> t -> t
    val union : t -> t -> t
    val inter : t -> t -> t
    val diff : t -> t -> t
    val compare : t -> t -> int
    val equal : t -> t -> bool
    val subset : t -> t -> bool
    val iter : (elt -> unit) -> t -> unit
    val fold : (elt -> 'a -> 'a) -> t -> 'a -> 'a
    val for_all : (elt -> bool) -> t -> bool
    val exists : (elt -> bool) -> t -> bool
    val filter : (elt -> bool) -> t -> t
    val partition : (elt -> bool) -> t -> t * t
    val cardinal : t -> int
    val elements : t -> elt list
    val min_elt : t -> elt
    val max_elt : t -> elt
    val choose : t -> elt
    val split : elt -> t -> t * bool * t
    val find : elt -> t -> elt
  end

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
