import os, sys, csv, logging

from funcy import *
from collections import namedtuple

import networkx as nx
import pyparsing
import lineparser
import grammar
import traversal

#ProgramLine = namedtuple('ProgramLine', ['line', 'is_series'])

class MoDeLFile:
    def __init__(self, filename):
        self.filename = filename
        # Load calibration
        self.heap = self.load_calibration()
        # Load file
        self.program = self.read_file(filename, master_file = True)
        # Include external files
        self.program = self.include_external(os.path.dirname(os.path.abspath(filename)), self.program)

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
            return lineparser.parse_lines(f.readlines())

    def include_external(self, abs_path, program):
        ret = []
        for l in program:
            if l[0:7] == "include":
                filename = os.path.join(abs_path, l[8:].strip())
                next_abs_path = os.path.dirname(filename)
                ret.append(self.include_external(next_abs_path, self.read_file(filename)))
            else:
                ret.append([l])
        return cat(ret)

    def build_dependency_graph(self, program):
        G = nx.DiGraph()
        #G.add_nodes_from([[k, {'equation': v['equation']}] for k, v in program.items()])
        variables = program.keys()
        dependencies = [v['dependencies'] for v in program.values()]
        # Also add exogenous variables to the graph
        #exogenous_variables = set(cat(dependencies)) - set(variables)
        #G.add_nodes_from(exogenous_variables)
        # Compute all directed edges
        edges = [ [d, start]
                  for start, deps in zip(variables, dependencies)
                  for d in deps ]
        #G.add_nodes_from(set(cat(dependencies)))
        G.add_edges_from(edges)
        return G

    def compile_line(self, line, heap, is_debug):
        ast = grammar.instruction.parseString(line)[0]
        generated_ast, heap = traversal.generate(traversal.compile_ast(ast, heap = heap), heap)
        return generated_ast, heap

    def compile_program(self, is_debug = False):
        program = {}
        temp = []
        for l in self.program:
            generated_ast, self.heap = self.compile_line(l, self.heap, is_debug)
            temp.append(generated_ast.generated)
            dependencies = traversal.dependencies(generated_ast)
            # Check if this variable already has an equation
            if len(dependencies.keys()) > 0 and dependencies.keys()[0] in program:
                raise NameError("The equation for variable {0} has already been specified. Use the @override keyword if you want to explictly replace it.".format(dependencies.keys()[0]))
            # Add this line to the program
            program.update(dependencies)
        graph = self.build_dependency_graph(program)
        sorted = nx.topological_sort(graph)
        # with open('keys.txt', 'w') as f:
        #     for n in sorted:
        #         f.write(n + '\n')
        nx.write_graphml(graph, 'dependency.graphml')
        return '\n'.join([program[var]['equation']
                          for var in sorted
                          if var in program and len(program[var]['equation']) > 0])
    #        return '\n'.join(cat([l for l in temp if len(l) > 0]))


if __name__ == "__main__":
    is_debug = len(sys.argv) > 1 and sys.argv[1] == "debug"

    if is_debug:
        logging.basicConfig(level=logging.DEBUG)

    try:
        # The code to be compiled is passed in file in.txt
        model = MoDeLFile("in.txt")
        # Compile and generate the output
        output = model.compile_program(is_debug)
    except pyparsing.ParseException as e:
        output = "Error\r\n" + str(e)
    except Exception as e:
        if is_debug:
            logging.exception("Error")
        output = "Error\r\n" + repr(e)

    # Writes the output, compiled code or error message to file out.txt
    with open("out.txt.prg", 'w') as f:
        f.write(output)

    # In debug mode, also write the output directly to the console
    # if is_debug:
    #     logging.debug(output)
