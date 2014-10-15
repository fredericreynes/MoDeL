from .. import lexer
from StringIO import StringIO

class TestLexer:
    def _test(self, input, output):
        assert lexer.Lexer(StringIO(input)).read() == output

    def _read_all(self, lexer):
        ret = []
        token = lexer.read()
        while not (token[0] is None):
            ret.append(token)
            token = lexer.read()
        return ret

    def _test_all(self, input, output):
        assert self._read_all(lexer.Lexer(StringIO(input))) == output

    def test_scans_integer(self):
        self._test("42", ('integer', '42'))
        self._test("-42", ('integer', '-42'))

    def test_scans_real(self):
        self._test("3.14159", ('real', '3.14159'))

    def test_scans_operator(self):
        self._test("+", ('operator', '+'))

    def test_scans_lists(self):
        self._test_all("01 02 03 04 \ 01 02",
                       [('integer', '01'),
                        ('integer', '02'),
                        ('integer', '03'),
                        ('integer', '04'),
                        ('backlash', '\\'),
                        ('integer', '01'),
                        ('integer', '02'),
                        ('newline', '')])

    def test_scans_expressions(self):
        self._test_all("42 + 3.14159 / 1981",
                       [('integer', '42'),
                        ('operator', '+'),
                        ('real', '3.14159'),
                        ('operator', '/'),
                        ('integer', '1981'),
                        ('newline', '')])
        self._test_all("42 and 3.14159 or 1981",
                       [('integer', '42'),
                        ('operator', 'and'),
                        ('real', '3.14159'),
                        ('operator', 'or'),
                        ('integer', '1981'),
                        ('newline', '')])
        self._test_all("K_n[s] <> 0",
                       [('name', 'K_n'),
                        ('lbracket', '['),
                        ('name', 's'),
                        ('rbracket', ']'),
                        ('operator', '<>'),
                        ('integer', '0'),
                        ('newline', '')])

    def test_scans_functions(self):
        self._test_all("d(log(Y[s]))",
                       [('name', 'd'),
                        ('lparen', '('),
                        ('name', 'log'),
                        ('lparen', '('),
                        ('name', 'Y'),
                        ('lbracket', '['),
                        ('name', 's'),
                        ('rbracket', ']'),
                        ('rparen', ')'),
                        ('rparen', ')'),
                        ('newline', '')])

    def test_scans_names(self):
        self._test("P", ('name', 'P'))
        self._test("EFER_n", ('name', 'EFER_n'))
        self._test("@elem", ('name', '@elem'))
        self._test("_test", ('name', '_test'))

    def test_scans_local_names(self):
        self._test("%list_com", ('local', '%list_com'))

    def test_scans_identifiers(self):
        self._test_all("P[c]",
                       [('name', 'P'),
                        ('lbracket', '['),
                        ('name', 'c'),
                        ('rbracket', ']'),
                        ('newline', '')])
        self._test_all("PRF[sm]{-1}",
                       [('name', 'PRF'),
                        ('lbracket', '['),
                        ('name', 'sm'),
                        ('rbracket', ']'),
                        ('lcurly', '{'),
                        ('integer', '-1'),
                        ('rcurly', '}'),
                        ('newline', '')])
        self._test_all("|V||O|",
                       [('pipe', '|'),
                        ('name', 'V'),
                        ('pipe', '|'),
                        ('pipe', '|'),
                        ('name', 'O'),
                        ('pipe', '|'),
                        ('newline', '')])

    def test_scans_formulas(self):
        self._test_all("@pv VA = sum(VA[s] on s)",
                       [('option', '@pv'),
                        ('name', 'VA'),
                        ('equal', '='),
                        ('name', 'sum'),
                        ('lparen', '('),
                        ('name', 'VA'),
                        ('lbracket', '['),
                        ('name', 's'),
                        ('rbracket', ']'),
                        ('keyword', 'on'),
                        ('name', 's'),
                        ('rparen', ')'),
                        ('newline', '')])

    def test_scans_strings(self):
        self._test("..\\model\\blocks", ('string', "..\\model\\blocks"))


    def test_scans_blocks(self):
        test = """GDP = 0

        #Comment

        Another := 15 123
        """
        self._test_all(test,
                       [('name', 'GDP'),
                        ('equal', '='),
                        ('integer', '0'),
                        ('newline', '\n\n'),
                        ('name', 'Another'),
                        ('assign', ':='),
                        ('integer', '15'),
                        ('integer', '123'),
                        ('newline', '\n')])