import os, sys, csv, logging

from funcy import *
from collections import namedtuple

import pyparsing
import lineparser
import grammar
import traversal

ProgramLine = namedtuple('ProgramLine', ['line', 'is_series'])

class MoDeLFile:
    def __init__(self, filename):
        self.filename = filename
        # Load calibration
        self.heap = self.load_calibration()
        # Load file
        self.program = self.read_file(filename, master_file = True)
        # Include external files
        self.program = self.include_external(os.path.dirname(os.path.abspath(filename)), self.program)

    def replace_assignments(self):
        self.program = [l.replace('==', '=') for l in self.program]

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
        if os.path.basename(filename) == os.path.basename(self.filename) and not master_file:
            raise Error("A file cannot include itself")
        # Update the current root for future possible includes
        with open(filename, "r") as f:
            return [ProgramLine(l, False) for l in lineparser.parse_lines(f.readlines())]

    def include_external(self, abs_path, program):
        ret = []
        for l in program:
            if l.line[0:7] == "include":
                filename = os.path.join(abs_path, l.line[8:].strip())
                next_abs_path = os.path.dirname(filename)
                ret.append(self.include_external(next_abs_path, self.read_file(filename)))
            else:
                ret.append([l])
        return cat(ret)

    def compile_line(self, line, heap, is_debug):
        ast = grammar.instruction.parseString(line)[0]
        if is_debug:
            logging.debug(ast)
        generated, heap = traversal.generate(traversal.compile_ast(ast, heap = heap), heap)
        return '\n'.join(generated), heap

    def compile_program(self, is_debug = False):
        compiled = []
        for lp in self.program:
            compiled_line, self.heap = self.compile_line(lp.line, self.heap, is_debug)
            compiled.append(compiled_line)
        return '\n'.join([l for l in compiled if len(l) > 0])


if __name__ == "__main__":
    # Option parsing
    is_debug = len(sys.argv) > 1 and sys.argv[1] == "debug"
    compile_as_series = len(sys.argv) > 1 and sys.asrgv[1] == "series"

    if is_debug:
        logging.basicConfig(level=logging.DEBUG)

    try:
        # The code to be compiled is passed in file in.txt
        model = MoDeLFile("in.txt")
        # If compiled as series, replace '==' with '='
        # and compile normally
        if compile_as_series:
            model.replace_assignments()
        # Compile and generate the output
        output = model.compile_program(is_debug)
    except pyparsing.ParseException as e:
        output = "Error\r\n" + str(e)
    except Exception as e:
        if is_debug:
            logging.exception("Error")
        output = "Error\r\n" + repr(e)

    # Writes the output, compiled code or error message to file out.txt
    with open("out.txt", 'w') as f:
        f.write(output)

    # In debug mode, also write the output directly to the console
    if is_debug:
        logging.debug(output)
