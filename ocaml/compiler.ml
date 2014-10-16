open Batteries
open Ast

let parse_string s = Parser.main Lexer.token (Lexing.from_string (s ^ "\n"))
(* let compile_string s = string_of_ast (parse_string s) *)

let _ =
  (* print_endline (compile_string "4 + 2 * 3") *)
  print_endline (dump (parse_string "45 := f(4 + 2 * 3, 42)"))
