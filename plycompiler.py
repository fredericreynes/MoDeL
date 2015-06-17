import plyyacc

def compile(program, heap):
    ast = plyyacc.parser.parse(program)

    # Go through statements
    for s in ast[1]:
        print s
        if s[1][0] == 'LocalDef':
            heap[s[1][1]] = s[1][2][1]

    print heap

if __name__ == "__main__":
    compile('%test := {"15", "05"}\n', {})
    print plyyacc.parser.parse("""t = X|O|[1, 2]{t-1} if test > 2 where i in %c
                          %test := {"15", "05"}
                          functionTest = function()
                          functionTest2 = function(hello[c] where (c, s) in ({"01"}, {"05"}), world)
                          """)
