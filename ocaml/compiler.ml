open Batteries
open Ast

let _ =
  (* let filename = "test_parser.txt" in *)
  (* let input = open_in filename in *)
  (* let lines  = List.of_enum (File.lines_of filename) in *)
  (* let lexbuf = Lexing.from_input input in *)
  (* let s = "45 := 42 + 6\nl := 06 15 test pouet\n45 := |V|[5 + d]{2006} * X|O| - f(4 + 2 * 3, 42)\n%pouet  :x= 42" in *)
  let s = "%list  := 01 02 03" in
  let lines = String.nsplit s "\n" in
  let lexbuf = Lexing.from_string s in
  try
    let parsed = Parser.main Lexer.token lexbuf in
    print_endline (dump parsed); apply_assignments parsed; print_endline (dump (Hashtbl.find heap "%list"))
  with
  | Parser.Error ->
     let pos = Lexing.lexeme_start_p lexbuf in
     print_endline (String.slice ~first:(max 0 (pos.pos_cnum - pos.pos_bol - 10))
				 ~last:(pos.pos_cnum - pos.pos_bol + 10)
				 (List.nth lines (pos.pos_lnum - 1)));
     print_endline "          ^";
     Printf.printf "At line %d, character %d: syntax error.\n%!" pos.pos_lnum (pos.pos_cnum - pos.pos_bol)
     ;
  (* IO.close_in input *)
