import os, sys, csv, time, random

import pyparsing
import grammar

# The formula to be compiled is passed in the first command line argument
# If no formula was passed, exit
if len(sys.argv) < 2:
    sys.exit(0)
code = sys.argv[1]

if code[0] == '"':
    code = code[1:-1]

code = code.strip()

# Load values of all variables
with open('tmp_all_vars.csv', 'rb') as csvfile:
    rows = list(csv.reader(csvfile))
    heap = dict(zip(rows[0],
                    [float(e) if e != 'NA' else
                     None for e in rows[2]]))

compiler_out = "_compiler_out"

def ensure_directory(_path):
    if not os.path.exists(_path):
        os.makedirs(_path)

ensure_directory(compiler_out)

# Name of the file where the output will be saved
filename = str(int(time.time())) + str(random.randint(0, 999)) + ".txt"

# Compilation
try:
    output = grammar.formula.parseString(code)[0].compile(heap)
except pyparsing.ParseException as e:
    output = "Error\r\n" + str(e)
except:
    output = "Error\r\n" + str(sys.exc_info()[0])

# Writes the output, compiled code or error message to a file in _compiler_out
with open(os.path.join(compiler_out, filename), 'w') as f:
    f.write(output)

# Prints the filename to stdout, so that eViews can then load it
print (filename)
