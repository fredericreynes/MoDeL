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
| [' ' '\t']*'+'[' ' '\t']*            { PLUS }
| [' ' '\t']*'-'[' ' '\t']*            { MINUS }
| [' ' '\t']*'*'[' ' '\t']*            { TIMES }
| [' ' '\t']*'/'[' ' '\t']*            { DIV }
|            '('[' ' '\t']*            { LPAREN }
| [' ' '\t']*')'                       { RPAREN }
|            '['[' ' '\t']*            { LBRACKET }
| [' ' '\t']*']'                       { RBRACKET }
|            '{'[' ' '\t']*            { LCURLY }
| [' ' '\t']*'}'                       { RCURLY }
| '|'                                  { PIPE }
| [' ' '\t']*'\\'[' ' '\t']*           { BACKSLASH }
| '\''                                 { read_string (Buffer.create 17) lexbuf }
| [' ' '\t']*','[' ' '\t']*            { COMMA }
| [' ' '\t']*'='[' ' '\t']*            { EQUAL }
| [' ' '\t']*":="[' ' '\t']*           { ASSIGN }
| [' ' '\t']+                          { WS }
| '\n'                                 { next_line lexbuf; EOL }
| '\r''\n'                             { next_line lexbuf; EOL }
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
