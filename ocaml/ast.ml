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

type statement =
  | Equation of expr * expr
  | AssignExpr of expr * expr
  | AssignLst of expr * lst


module Heap = Map.Make(String)

let h = Heap.empty

(* let apply_assignments stmts = *)
(*   List.iter (fun s -> *)
(* 	    | AssignExpr e -> *)
(* 	       let (lhs, rhs) = e in *)

(* 	    ) stmts *)
