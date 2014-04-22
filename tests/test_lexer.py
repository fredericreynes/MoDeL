from .. import lexer
from StringIO import StringIO

class TestLexer:
    def _test(self, input, output):
        assert lexer.Lexer(StringIO(input)).read() == output

    def test_scans_integer(self):
        self._test("42", ('int', '42'))

    def test_scans_real(self):
        self._test("3.14159", ('real', '3.14159'))
