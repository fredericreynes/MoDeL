rm compiler.byte
ocamlbuild -package batteries -use-menhir compiler.byte
ocamlrun compiler.byte