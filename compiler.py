import os, sys, csv

import pyparsing
import grammar

# The code to be compiled is passed in file in.txt
with open("in.txt", "r") as f:
    code = f.readline().strip()

if code[0] == '"':
    code = code[1:-1]

# Load values of all variables
with open('tmp_all_vars.csv', 'rb') as csvfile:
    rows = list(csv.reader(csvfile))
    heap = dict(zip(rows[0],
                    [float(e) if e != 'NA' else
                     None for e in rows[2]]))

# Compilation
if len(sys.argv) > 1:
    output = grammar.formula.parseString(code)[0].compile(heap)
else:
    try:
        output = grammar.formula.parseString(code)[0].compile(heap)
    except pyparsing.ParseException as e:
        output = "Error\r\n" + str(e)
    except Exception as e:
        output = "Error\r\n" + repr(e)

# Writes the output, compiled code or error message to file out.txt
with open("out.txt", 'w') as f:
    f.write(output)
