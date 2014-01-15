class AST:
    def __init__(self, nodetype, children):
        self.nodetype = nodetype
        self.children = children
        self.compiled = None
        self.generated = None

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

    def call_node_method(self, ast):
        method_name = "n_" + ast.nodetype
        if ast.is_immediate and hasattr(self, "n_immediate"):
            self.n_immediate(ast)
        if hasattr(self, method_name):
            getattr(self, "n_" + ast.nodetype)(ast)
        else:
            self.default(ast)

    def default(self, ast):
        pass

    def traverse(self, ast):
        self.call_node_method(ast)

        if not ast.is_immediate:
            for c in ast.children:
                if not (c is None or c.is_immediate):
                    self.traverse(c)


class NodeCount(ASTTraversal):
    def default(self, ast):
        ast.compiled = ast.nodetype + ": " + str(len(ast.children))

class Compile(ASTTraversal):
    def n_immediate(self, ast):
        ast.compiled = ast.children[0]

    def n_list(self, ast):
        ast.compiled = [e for e in ast.children[0] if e not in ast.children[1]]

    def default(self, ast):
        ast.compiled = [c.compiled for c in ast.children]

def compile(ast):
    Compile(ast)
    return ast.compiled
