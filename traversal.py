from itertools import product, chain, tee
from funcy import *
import code

class AST:
    def __init__(self, nodetype, children):
        self.nodetype = nodetype
        self.children = children
        self.compiled = None
        self.as_value = False

    def __getitem__(self, i):
        return self.children[i]

    def __iter__(self):
        return iter(self.children)

    def __len__(self):
        return len(self.children)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return all(selfc == otherc for (selfc, otherc) in zip(self.children, other.children))
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    @property
    def is_immediate(self):
        return len(self.children) == 1 and not isinstance(self.children[0], AST)

    @property
    def is_none(self):
        return self.nodetype == "none"

    @property
    def immediate(self):
        if self.is_immediate:
            return self.children[0]
        else:
            raise TypeError

    def __str__(self):
        base = self.nodetype + ": "
        if self.is_immediate:
            return base + repr(self.children[0])
        else:
            return base + '(' + ', '.join([str(e) for e in self.children]) + ')'

ASTNone = AST('none', [])


def compile_ast(ast, bindings = {}, use_bindings = False, as_value = False):
    ast.as_value = as_value

    if ast.is_immediate:
        imm = ast.immediate
        # Always use bindings for loop counters
        use_bindings = use_bindings or str(imm)[0] == '$'
        if use_bindings and imm in bindings and ast.nodetype == "variableName":
            ast.compiled = bindings[imm]
        else:
            ast.compiled = imm

    elif ast.nodetype == "formula":
        # First compile iterators
        if not ast.children[3] is None:
            iterators = [compile_ast(c).compiled for c in ast.children[3:]]
            # Get the lists only
            all_lists = [iter['lists'] for iter in iterators]
            # Cartesian product of all the iterators' lists
            prod = product(*all_lists)
            # Names of all the iterators and associated loop counters
            all_names = cat(iter['names'] for iter in iterators)
            # Build the final list containing all the bindings
            all_bindings = [dict(zip(all_names, cat(p))) for p in prod]
        else:
            all_bindings = [{}]

        # Apply external bindings, if any
        if len(bindings) > 0:
            all_bindings = [merge(locals, bindings) for locals in all_bindings]

        # Check for the price-value option
        price_value = not ast.children[0] is None

        # Then compile conditions
        if not ast.children[2] is None:
            conditions = (compile_ast(ast.children[2], locals) for locals in all_bindings)
            # If price-value is set, should generate a second set of equations - but conditions should remain unchanged, thus we just repeat them
            if price_value:
                conditions = chain(conditions, (compile_ast(ast.children[2], locals) for locals in all_bindings))
        else:
            conditions = []

        # Finally compile the equation / expression for each binding
        equations = (compile_ast(ast.children[1], locals, as_value = as_value) for locals in all_bindings)
        # If price-value is set, should generate a second set of equations, in value form
        if price_value:
            equations = chain(equations, (compile_ast(ast.children[1], locals, as_value = True) for locals in all_bindings))

        ast.compiled = { 'conditions': conditions,
                         'equations': equations }

    elif ast.nodetype == "function":
        name = compile_ast(ast.children[0]).compiled

        if name == "sum":
            generator = lambda toks: "0 + " + ' + '.join(toks)
        elif name == "value":
            as_value = True
            generator = lambda toks: toks[0]
        else:
            generator = lambda toks: ast.compiled['name'] + '(' + ', '.join(toks) + ')'

        ast.compiled = { 'name': name,
                         'generator': generator,
                         'arguments': [compile_ast(c, bindings, True, as_value) for c in ast.children[1:]] }

    elif ast.nodetype in ["index", "placeholder", "timeOffset"]:
        ast.compiled = [compile_ast(c, bindings, True) for c in ast.children]

    elif ast.nodetype in ["identifier", "array"]:
        # The as_value flag should not propagate downwards inside the identifier and array nodetypes
        if as_value:
            as_value = False
        ast.compiled = [compile_ast(c, bindings, use_bindings, as_value) for c in ast.children]

    elif ast.nodetype == "iterator":
        # If the iterator is correctly defined, there are as many iterator names
        # as there are lists. So we divide the children in halves
        list_count = len(ast.children) / 2
        names = [compile_ast(c).compiled for c in ast.children[:list_count]]
        lists = [compile_ast(c).compiled for c in ast.children[list_count:]]
        # HACK !! Used for the loop counters
        listBaseLength = [len(lst.children[0].children) for lst in ast.children[list_count:]]
        # Add the loop counters
        names = names + ['$' + name for name in names]
        lists = lists + [range(1, n + 1) for n in listBaseLength]
        ast.compiled = { 'names': names,
                         'lists': zip(*lists) }

    elif ast.nodetype == "listBase":
        ast.compiled = [compile_ast(c).compiled for c in ast.children]

    elif ast.nodetype == "list":
        base = compile_ast(ast.children[0]).compiled
        excluded = compile_ast(ast.children[1]).compiled
        ast.compiled = [e for e in base if e not in excluded]

    elif ast.is_none:
        ast.compiled = ASTNone

    else:
        ast.compiled = [compile_ast(c, bindings, use_bindings, as_value) for c in ast.children]

    return ast

def value_form(str, flag):
    if flag:
        return 'P' + str + ' * ' + str
    else:
        return str

def generate(ast, heap = {}):
    if ast.is_immediate:
        ret = str(ast.compiled)
        if ast.nodetype == "variableName":
            return value_form(ret, ast.as_value)
        else:
            return ret

    elif ast.nodetype == "array":
        ret = generate(ast.children[0])
        if not ast.children[1].is_none:
            ret += '_' + generate(ast.children[1])
        if not ast.children[2].is_none:
            ret += generate(ast.children[2])
        return value_form(ret, ast.as_value)

    elif ast.nodetype == "identifier":
        return value_form(''.join(generate(c) for c in ast.compiled), ast.as_value)

    elif ast.nodetype == "condition":
        # All variables in the heap should be uppercase
        return eval(generate(ast.compiled[0]).upper(), heap)

    elif ast.nodetype == "expression":
        return ' '.join(generate(c, heap) for c in ast.compiled)

    elif ast.nodetype == "equation":
        return generate(ast.children[0], heap) + ' = ' + generate(ast.children[1], heap)

    elif ast.nodetype == "formula":
        conditions = [generate(cond, heap) for cond in ast.compiled['conditions']]
        equations = [generate(eq, heap) for eq in ast.compiled['equations']]
        if len(conditions) > 0:
            return [eq for eq, cond in zip(equations, conditions) if cond]
        else:
            return equations

    elif ast.nodetype == "function":
        generated_args = [generate(a, heap) for a in ast.compiled['arguments']]
        # Special case if there is only one argument, parsed as a formula but behaving like an expression
        if len(generated_args) == 1 and isinstance(generated_args[0], list):
            generated_args = generated_args[0]
        return ast.compiled['generator'](generated_args)

    elif ast.nodetype == "placeholder":
        return ''.join(generate(c) for c in ast.compiled)

    elif ast.nodetype == "index":
        return '_'.join(generate(c, heap) for c in ast.compiled)

    elif ast.nodetype == "timeOffset":
        return '(' + generate(ast.children[0]) + ')'

    elif ast.is_none:
        return ""
