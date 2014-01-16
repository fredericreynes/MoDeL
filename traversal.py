class AST:
    def __init__(self, nodetype, children):
        self.nodetype = nodetype
        self.children = children
        self.compiled = None
        self.generated = None

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


class ASTTraversal:
    def __init__(self, ast):
        self.traverse(ast)

    def safe_call(self, method, arg):
        if hasattr(self, method):
            getattr(self, method)(arg)

    def call_node_method(self, ast, suffix):
        method_name = "n_" + ast.nodetype + "_" + suffix

        if ast.is_immediate:
            self.safe_call("n_immediate_" + suffix, ast)
            self.safe_call(method_name, ast)
        elif hasattr(self, method_name):
            getattr(self, method_name)(ast)
        else:
            if suffix == "pre":
                self.default_pre(ast)
            else:
                self.default_post(ast)

    def default_pre(self, ast):
        pass

    def default_post(self, ast):
        pass

    def traverse(self, ast):
        self.call_node_method(ast, "pre")

        if not ast.is_immediate:
            for c in ast.children:
                if not (c is None or c.is_immediate):
                    self.traverse(c)

        self.call_node_method(ast, "post")


class NodeCount(ASTTraversal):
    def default(self, ast):
        ast.compiled = ast.nodetype + ": " + str(len(ast))

class Compile(ASTTraversal):
    def n_immediate_post(self, ast):
        ast.compiled = ast[0]

    def n_list_post(self, ast):
        if ast.children[1] is None:
            ast.compiled = ast.children[0]
        else:
            print ast.children[0]
            print ast.children[1]
            ast.compiled = [e for e in ast.children[0] if e not in ast.children[1]]

def compile(ast):
    Compile(ast)
    return ast.compiled
