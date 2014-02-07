import os, sys, csv

import pyparsing
import lineparser
import grammar
import traversal

def load_file(filename):
    with open(filename, "r") as f:
        return lineparser.parse_lines(f.readlines())

def compilation(code, heap):
    ast = grammar.formula.parseString(code)[0]
    return '\n'.join(traversal.generate(traversal.compile_ast(ast), heap))

# Load values of all variables
with open('tmp_all_vars.csv', 'rb') as csvfile:
    rows = list(csv.reader(csvfile))
    heap = dict(zip(rows[0],
                    [float(e) if e != 'NA' else
                     None for e in rows[2]]))

# The code to be compiled is passed in file in.txt
program = load_file("in.txt")

# Compilation
if len(sys.argv) > 1:
    output = '\n'.join([compilation(line, heap) for line in program])
else:
    try:
        output = '\n'.join([compilation(line, heap) for line in program])
    except pyparsing.ParseException as e:
        output = "Error\r\n" + str(e)
    except Exception as e:
        output = "Error\r\n" + repr(e)

# Writes the output, compiled code or error message to file out.txt
with open("out.txt", 'w') as f:
    f.write(output)
