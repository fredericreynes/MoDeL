from .. import parser
from StringIO import StringIO

class TestCompiler:

    def _compile(self, str):
        return parser.Compiler(StringIO(str))

    def test_compiles_assignments(self):
        out = self._compile("%test := 01 02 03 04")
        assert out.heap == {'%test': ['01', '02', '03', '04']}

    def test_compiles_placeholder(self):
        self._compile("test = |V|")
        self._compile("test = |V||O|")
        self._compile("test = test|V||O|")

    def test_compiles_expression(self):
        self._compile("test = a + b - c")
        self._compile("test = %a + b[c]")
        self._compile("test = %a + b[c, g, j]")
        self._compile("test = %a + b[c, g, j]")
        self._compile("test = a + func(pouet) - c")
