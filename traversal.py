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

ASTNone = AST('none', [])


def compile_ast(ast, bindings = {}):
    if ast.is_immediate:
        ast.compiled = ast.immediate

    elif ast.nodetype == "listBase":
        ast.compiled = [compile_ast(c) for c in ast.children]

    elif ast.nodetype == "list":
        base = compile_ast(ast.children[0])
        excluded = compile_ast(ast.children[1])
        ast.compiled = [e for e in base if e not in excluded]

    elif ast.nodetype == "placeholder":
        ast.compiled = bindings[compile_ast(ast.children[0])]

    elif ast.nodetype == "none":
        ast.compiled = ASTNone

    return ast.compiled


