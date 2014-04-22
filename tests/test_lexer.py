from .. import lexer
from StringIO import StringIO

class TestLexer:
    def _test(self, input, output):
        assert lexer.Lexer(StringIO(input)).read() == output

    def _test_all(self, input, output):
        assert lexer.Lexer(StringIO(input)).read_all() == output

    def test_scans_integer(self):
        self._test("42", ('integer', '42'))
        self._test("-42", ('integer', '-42'))

    def test_scans_real(self):
        self._test("3.14159", ('real', '3.14159'))

    def test_scans_operator(self):
        self._test("+", ('operator', '+'))

    def test_scans_arithmetic_expression(self):
        self._test_all("42 + 3.14159 / 1981",
                       [('integer', '42'),
                        ('operator', '+'),
                        ('real', '3.14159'),
                        ('operator', '/'),
                        ('integer', '1981')])

    def test_scans_names(self):
        self._test("P", ('name', 'P'))
        self._test("EFER_n", ('name', 'EFER_n'))
        self._test("@elem", ('name', '@elem'))
        self._test("_test", ('name', '_test'))

    def test_local_names(self):
        self._test("%list_com", ('local', '%list_com'))

    def test_scans_identifiers(self):
        self._test_all("P[c]",
                       [('name', 'P'),
                        ('lbracket', '['),
                        ('name', 'c'),
                        ('rbracket', ']')])
        self._test_all("PRF[sm]{-1}",
                       [('name', 'PRF'),
                        ('lbracket', '['),
                        ('name', 'sm'),
                        ('rbracket', ']'),
                        ('lcurly', '{'),
                        ('integer', '-1'),
                        ('rcurly', '}')])
