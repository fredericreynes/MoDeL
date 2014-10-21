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
| [' ' '\t']*','[' ' '\t']*            { COMMA }
| [' ' '\t']*'='[' ' '\t']*            { EQUAL }
| [' ' '\t']*":="[' ' '\t']*           { ASSIGN }
| [' ' '\t']+                          { WS }
| '\n'                                 { next_line lexbuf; EOL }
| '\r''\n'                             { next_line lexbuf; EOL }
| eof                                  { EOF }
