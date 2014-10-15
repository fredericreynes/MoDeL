(* File calc.ml *)
open Ast

let _ =
  try
    let lexbuf = Lexing.from_channel stdin in
    while true do
      let result = Parser.main Lexer.token lexbuf in
      print_endline (string_of_ast result) (* ; flush stdout *)
    done
  with Lexer.Eof ->
    exit 0
