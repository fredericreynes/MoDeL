(* File lexer.mll *)
{
  open Parser        (* The type token is defined in parser.mli *)
  open Lexing

  let next_line lexbuf =
    let pos = lexbuf.lex_curr_p in
    lexbuf.lex_curr_p <-
      { pos with pos_bol = pos.pos_cnum;
		 pos_lnum = pos.pos_lnum + 1
      }
}
rule token = parse
| ['0'-'9']+ as lxm                    { INT(lxm) }
| ['_' 'a'-'z''A'-'Z''0'-'9']+ as id   { ID(id) }
| '%'['_' 'a'-'z''A'-'Z''0'-'9']+ as l { LOCAL(l) }
| '+'                                  { PLUS }
| '-'                                  { MINUS }
| '*'                                  { TIMES }
| '/'                                  { DIV }
| '('                                  { LPAREN }
| ')'                                  { RPAREN }
| '['                                  { LBRACKET }
| ']'                                  { RBRACKET }
| '{'                                  { LCURLY }
| '}'                                  { RCURLY }
| '|'                                  { PIPE }
| '\\'                                 { BACKSLASH }
| '\''                                 { read_string (Buffer.create 17) lexbuf }
| ','                                  { COMMA }
| '='                                  { EQUAL }
| ":="                                 { ASSIGN }
| [' ' '\t']+                          { token lexbuf }
| '\n' | '\r' | "\r\n"                 { next_line lexbuf; EOL }
| eof                                  { EOF }
and read_string buf =
  parse
  | '\''      { STRING (Buffer.contents buf) }
  | '\\' '/'  { Buffer.add_char buf '/'; read_string buf lexbuf }
  | '\\' '\\' { Buffer.add_char buf '\\'; read_string buf lexbuf }
  | '\\' 'b'  { Buffer.add_char buf '\b'; read_string buf lexbuf }
  | '\\' 'f'  { Buffer.add_char buf '\012'; read_string buf lexbuf }
  | '\\' 'n'  { Buffer.add_char buf '\n'; read_string buf lexbuf }
  | '\\' 'r'  { Buffer.add_char buf '\r'; read_string buf lexbuf }
  | '\\' 't'  { Buffer.add_char buf '\t'; read_string buf lexbuf }
  | [^ '\'' '\\']+
    { Buffer.add_string buf (Lexing.lexeme lexbuf);
      read_string buf lexbuf
    }
  (* | _ { raise (SyntaxError ("Illegal string character: " ^ Lexing.lexeme lexbuf)) } *)
  (* | eof { raise (SyntaxError ("String is not terminated")) } *)
