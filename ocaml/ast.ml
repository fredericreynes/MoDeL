type operator =
  | Plus
  | Minus
  | Times
  | Div

type ast =
  | Number of int
  | BinOp of operator * ast * ast

let test = BinOp (Plus, BinOp (Times, Number 4, Number 2), Number 3)

let string_of_operator = function
    Plus -> "+"
  | Minus -> "-"
  | Times -> "*"
  | Div -> "/"

let rec string_of_ast = function
    Number x -> string_of_int x
  | BinOp(op, x, y) -> String.concat " " ["("; string_of_ast x; string_of_operator op; string_of_ast y; ")"]

let () = print_endline (string_of_ast test)
