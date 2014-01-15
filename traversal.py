class ASTTraversal:
    def __init__(self, ast):
        self.traverse(ast)

    def call_node_method(self, ast):
        method_name = "n_" + ast.nodetype
        if hasattr(self, method_name):
            getattr(self, "n_" + ast.nodetype)(ast)
        else:
            self.default(ast)

    def default(self, ast):
        pass

    def traverse(self, ast):
        self.call_node_method(ast)

        for c in ast.children:
            if not (c is None or c.is_immediate):
                self.traverse(c)


class NodeCount(ASTTraversal):
    def default(self, ast):
        print ast.nodetype + ": " + str(len(ast.children))

