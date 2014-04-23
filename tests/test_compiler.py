from .. import parser
from StringIO import StringIO

class TestCompiler:

    def test_compiles_assignments(self):
        out = parser.Compiler(StringIO("%test := 01 02 03 04"))
        assert out.heap == {'%test': ['01', '02', '03', '04']}
