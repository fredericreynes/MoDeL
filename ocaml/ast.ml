type ast =
  | Number of int
  | Plus of ast * ast
  | Minus of ast * ast
  | Times of ast * ast
  | Div of ast * ast

let test = Plus(Number 4, Number 2)

let rec string_of_ast = function
    Number x -> string_of_int x
  | Plus(x, y) -> string_of_ast x ^ " + " ^ string_of_ast y
  | Minus(x, y) -> string_of_ast x ^ " - " ^ string_of_ast y
  | Times(x, y) -> string_of_ast x ^ " * " ^ string_of_ast y
  | Div(x, y) -> string_of_ast x ^ " / " ^ string_of_ast y

let () = print_endline (string_of_ast test)
