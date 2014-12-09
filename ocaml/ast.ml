module StringSet = Set.Make(String)

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

type sset = StringSet.t

type sset_expr =
  | SSet of sset
  | BinOp of operator * sset_expr * sset_expr
  | Local of string

type statement =
  | Equation of expr * expr
  | AssignExpr of expr * expr
  | AssignSSet of expr * sset_expr


let heap = Hashtbl.create 10000

(* let h = Heap.add "Test" ["world"; "42"]  h *)

let string_of_expr = function
    Number n -> string_of_int n
  | Local id -> id
  | _ -> "Not a local variable"

let rec compile_sset_expr = function
    SSet ss -> ss
  | BinOp(Plus, sel, ser) -> StringSet.union (compile_sset_expr sel) (compile_sset_expr ser)
  | BinOp(Minus, sel, ser) -> StringSet.diff (compile_sset_expr sel) (compile_sset_expr ser)
  | Local l -> Hashtbl.find heap l

let sset_of_lst a_lst =
    List.fold_right StringSet.add a_lst StringSet.empty

let apply_assignments stmts =
  List.iter (fun s -> match s with
		      | AssignSSet (lhs, rhs) -> Hashtbl.add heap (string_of_expr lhs) (compile_sset_expr rhs)
		      | _ -> print_endline "Not an assignment"
	    ) stmts
