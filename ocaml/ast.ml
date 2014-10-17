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

type lst = string list

type statement =
  | Equation of expr * expr
  | AssignExpr of expr * expr
  | AssignLst of expr * lst

let test = BinOp (Plus, BinOp (Times, Number 4, Number 2), Number 3)

let string_of_operator = function
    Plus -> "+"
  | Minus -> "-"
  | Times -> "*"
  | Div -> "/"

let rec string_of_ast = function
    Number x -> string_of_int x
  | UnOp(op, x) -> String.concat " " ["-("; string_of_ast x; ")"]
  | BinOp(op, x, y) -> String.concat " " ["("; string_of_ast x; string_of_operator op; string_of_ast y; ")"]

(* let () = print_endline (string_of_ast test) *)
