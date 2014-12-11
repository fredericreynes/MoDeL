type t = (string * int) list

let rec range a b =
  if a > b then []
  else a :: range (a + 1) b

let of_list l =
  List.combine l (range 1 (List.length l))

let diff l1 l2 =
  let (l2_str, _) = List.split l2 in
  List.filter (fun x -> let (s, _) = x in not (List.mem s l2_str)) l1

let rec shift_index l n = match l with
    (s, i) :: t -> (s, i + n) :: (shift_index t n)
  | [] -> []

let join l1 l2 =
  l1 @ (shift_index l2 (List.length l1) )
