import os, sys, csv

from funcy import *

import pyparsing
import lineparser
import grammar
import traversal

class MoDeLFile:
    def __init__(self, filename):
        self.filename = filename
        # Load calibration
        self.heap = self.load_calibration()
        # Load file
        self.program = self.read_file(filename, master_file = True)
        # Include external files
        self.program = self.include_external(self.program)

    def load_calibration(self):
        # Load values of all variables
        with open('_tmp_all_vars.csv', 'rb') as csvfile:
            rows = list(csv.reader(csvfile))
            return dict(zip(rows[0],
                        [float(e) if e != 'NA' else
                         None for e in rows[2]]))

    def read_file(self, filename, master_file = False):
        # If the filename has no extension,
        # appends the MoDeL extension to it
        if os.path.splitext(filename)[-1] == '':
            filename += '.mdl'
        # Check for self-inclusion
        if filename == self.filename and not master_file:
            raise Error("A file cannot include itself")
        with open(filename, "r") as f:
            return lineparser.parse_lines(f.readlines())

    def include_external(self, program):
        return cat([self.read_file(l[8:].strip()) if l[0:7] == "include"
                    else [l]
                    for l in program])

    def compile_line(self, line, heap):
        ast = grammar.instruction.parseString(line)[0]
        generated, heap = traversal.generate(traversal.compile_ast(ast, heap = heap), heap)
        return '\n'.join(generated), heap

    def compile_program(self):
        compiled = []
        for line in self.program:
            compiled_line, self.heap = self.compile_line(line, self.heap)
            compiled.append(compiled_line)
        return '\n'.join([l for l in compiled if len(l) > 0])


if __name__ == "__main__":
    try:
        # The code to be compiled is passed in file in.txt
        model = MoDeLFile("in.txt")
        # Compile and generate the output
        output = model.compile_program()
    except pyparsing.ParseException as e:
        output = "Error\r\n" + str(e)
    except Exception as e:
        output = "Error\r\n" + repr(e)

    # Writes the output, compiled code or error message to file out.txt
    with open("out.txt", 'w') as f:
        f.write(output)

    # In debug mode, also write the output directly to the console
    if len(sys.argv) > 1:
        print output
