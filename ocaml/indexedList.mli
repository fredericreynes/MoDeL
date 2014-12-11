type t = (string * int) list

val of_list : 'a list -> ('a * int) list

val diff : ('a * int) list -> ('a * int) list -> ('a * int) list

val join : ('a * int) list -> ('a * int) list -> ('a * int) list
