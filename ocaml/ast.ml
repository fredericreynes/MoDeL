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
  | Equation of expr * full_expr
  | AssignExpr of expr * expr
  | AssignLst of expr * lst_expr


let heap = Hashtbl.create 10000

(* let h = Heap.add "Test" ["world"; "42"]  h *)

let string_of_expr = function
    Number n -> string_of_int n
  | Local id -> id
  | _ -> "Not a local variable"


let rec compile_lst_expr = function
    Lst l -> l
  | BinOp(Plus, lel, ler) -> IndexedList.join (compile_lst_expr lel) (compile_lst_expr ler)
  | BinOp(Minus, lel, ler) -> IndexedList.diff (compile_lst_expr lel) (compile_lst_expr ler)
  | Local l -> Hashtbl.find heap l

let apply_assignments stmts =
  List.iter (fun s -> match s with
		      | AssignLst (lhs, rhs) -> Hashtbl.add heap (string_of_expr lhs) (compile_lst_expr rhs)
		      | _ -> print_endline "Not an assignment"
	    ) stmts
