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


let heap = Hashtbl.create 10000

(* let h = Heap.add "Test" ["world"; "42"]  h *)

let string_of_expr = function
    Local id -> id
  | _ -> "Not a local variable"

let apply_assignments stmts =
  List.iter (fun s -> match s with
		      | AssignLst (lhs, rhs) -> Hashtbl.add heap (string_of_expr lhs) rhs
		      | _ -> print_endline "Not an assignment"
	    ) stmts
